import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory, gettempdir
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"
REID_NAME = "person-reidentification-retail-0277"
REID_URL = (
    "https://storage.openvinotoolkit.org/repositories/open_model_zoo/"
    f"2023.0/models_bin/1/{REID_NAME}/FP16"
)
MODEL_FILES = {
    "yolo11n.pt": (
        "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt",
        "a8a7765b8a0d8e296934aa712c225653c304e2938f72a30cfcca042a4ca2b4db50c9b4da888d132e4a273fa8a8a64db2",
    ),
    f"{REID_NAME}.xml": (
        f"{REID_URL}/{REID_NAME}.xml",
        "554b403108fea776cb54c971c4c8acfaaeaae3884b5945eefbcbad8b9ed3c84f0382cb72c666c02c07129826a668d79e",
    ),
    f"{REID_NAME}.bin": (
        f"{REID_URL}/{REID_NAME}.bin",
        "0466aa71c44a14aa902a609c6500f4bc087cabbfa09c1e5bfb309f0a7e89fcdd9971e0359663e31803e3611bfa4d2353",
    ),
}


def parse_camera(value):
    camera_id, equals, name = value.partition("=")
    if not equals or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,31}", camera_id):
        raise argparse.ArgumentTypeError("camera must be CAMERA-ID=PATH")
    path = Path(name).resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"video does not exist: {path}")
    return camera_id, path


def parse_args():
    parser = argparse.ArgumentParser(description="Track people across synchronized video files.")
    parser.add_argument("--camera", action="append", type=parse_camera, required=True,
                        help="CAMERA-ID=PATH, repeat once per synchronized video")
    parser.add_argument("--output", type=Path, help="new video directory (default: AI/output/<time>)")
    parser.add_argument("--tracking", type=Path, help="new JSON file (default: AI/output/<video-directory>.json)")
    parser.add_argument("--fps", type=int, default=12, help="output frames per second (default: 12)")
    args = parser.parse_args()
    if len(args.camera) < 2 or len({name.lower() for name, _ in args.camera}) != len(args.camera):
        parser.error("supply at least two cameras with distinct IDs")
    if args.fps <= 0:
        parser.error("--fps must be positive")
    args.output = (args.output or ROOT / "output" / datetime.now().strftime("%Y%m%d-%H%M%S")).resolve()
    args.tracking = (args.tracking or ROOT / "output" / f"{args.output.name}.json").resolve()
    if args.tracking.suffix.lower() != ".json" or args.tracking.is_relative_to(args.output):
        parser.error("--tracking must be a .json file outside the video directory")
    if args.output.exists():
        parser.error(f"output already exists: {args.output}")
    if args.tracking.exists():
        parser.error(f"tracking file already exists: {args.tracking}")
    return args


def prepare_models():
    MODEL_DIR.mkdir(exist_ok=True)
    for name, (url, expected_hash) in MODEL_FILES.items():
        destination = MODEL_DIR / name
        if destination.is_file() and hashlib.sha384(destination.read_bytes()).hexdigest() == expected_hash:
            continue
        print(f"Downloading {name}", flush=True)
        temporary = None
        try:
            with NamedTemporaryFile(dir=MODEL_DIR, delete=False) as stream:
                temporary = Path(stream.name)
                digest = hashlib.sha384()
                with urlopen(url, timeout=60) as response:
                    while chunk := response.read(1024 * 256):
                        stream.write(chunk)
                        digest.update(chunk)
            if digest.hexdigest() != expected_hash:
                raise ValueError(f"download checksum mismatch: {name}")
            temporary.replace(destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def cpu_detector(weights, image_size):
    from ultralytics import YOLO

    destination = weights.parent / f"{weights.stem}-{image_size}_openvino_model"
    if not destination.is_dir():
        with TemporaryDirectory(prefix=".export-", dir=weights.parent) as directory:
            copy = Path(directory) / weights.name
            shutil.copyfile(weights, copy)
            exported = YOLO(str(copy)).export(format="openvino", imgsz=image_size, half=True, device="cpu")
            try:
                Path(exported).rename(destination)
            except OSError:
                if not destination.is_dir():
                    raise
    return destination


def normalize_video(ffmpeg, source, target, fps):
    subprocess.run([
        ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(source),
        "-map", "0:v:0", "-an", "-sn", "-dn",
        "-vf", f"fps={fps},pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v", "libx264", "-threads", "2", "-pix_fmt", "yuv420p", "-preset", "fast",
        "-crf", "19", "-movflags", "+faststart", str(target),
    ], check=True)


def build_session(cameras, global_ids, fps):
    tracks = {}
    for camera in cameras:
        boxes = defaultdict(dict)
        tracks[camera.id] = boxes
        for track in camera.tracks:
            global_id = global_ids[camera.id, track.local_id]
            if not boxes[global_id].keys().isdisjoint(track.boxes):
                raise ValueError(f"{camera.id}: overlapping tracks for Global ID {global_id}")
            boxes[global_id].update(track.boxes)
    return {
        "version": 1,
        "fps": fps,
        "cameras": [
            {"id": camera.id, "file": camera.file, "width": camera.width, "height": camera.height,
             "frameCount": camera.frame_count}
            for camera in cameras
        ],
        "tracks": tracks,
    }


def format_tracking(data):
    text = json.dumps(data, indent=2, allow_nan=False)
    return re.sub(r"\[\n\s*(-?\d+),\s+(-?\d+),\s+(-?\d+),\s+(-?\d+)\s*\]",
                  r"[\1, \2, \3, \4]", text) + "\n"


def run(args):
    cache = Path(gettempdir()) / "cap28-reid"
    cache.mkdir(exist_ok=True)
    os.environ.setdefault("YOLO_CONFIG_DIR", str(cache))

    import imageio_ffmpeg
    import torch
    from reidentify import AppearanceEncoder, associate
    from track_video import track_video

    prepare_models()
    threads = min(4, os.cpu_count() or 1)
    torch.set_num_threads(threads)
    image_size = 320
    weights = cpu_detector(MODEL_DIR / "yolo11n.pt", image_size)
    encoder = AppearanceEncoder(MODEL_DIR / f"{REID_NAME}.xml", threads)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".reid-", dir=args.output.parent) as temp:
        stage = Path(temp) / "session"
        stage.mkdir()
        cameras = []
        for index, (camera_id, source) in enumerate(args.camera, 1):
            video = stage / f"camera-{index:02}.mp4"
            print(f"{camera_id}: converting {source.name} and tracking people", flush=True)
            normalize_video(ffmpeg, source, video, args.fps)
            camera = track_video(camera_id, video, weights, encoder, args.fps, image_size)
            if cameras and camera.frame_count != cameras[0].frame_count:
                raise ValueError(f"{camera_id}: expected {cameras[0].frame_count} synchronized frames, "
                                 f"decoded {camera.frame_count}")
            cameras.append(camera)
            print(f"{camera_id}: {camera.frame_count} frames, {len(camera.tracks)} local tracks", flush=True)

        local_tracks = [track for camera in cameras for track in camera.tracks]
        global_ids = associate(local_tracks, 0.65)
        data = build_session(cameras, global_ids, args.fps)
        args.tracking.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".reid-", dir=args.tracking.parent) as tracking_temp:
            staged_tracking = Path(tracking_temp) / "tracking.json"
            staged_tracking.write_text(format_tracking(data), encoding="utf-8")
            os.link(staged_tracking, args.tracking)
            try:
                stage.rename(args.output)
            except OSError:
                args.tracking.unlink()
                raise

    print(f"Videos: {args.output}\nTracking ({len(set(global_ids.values()))} global IDs): {args.tracking}", flush=True)


if __name__ == "__main__":
    try:
        run(parse_args())
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f"Re-ID failed: {error}")
