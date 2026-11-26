from dataclasses import dataclass, field
from pathlib import Path
import numpy as np


Box = tuple[int, int, int, int]


@dataclass
class Track:
    camera_id: str
    local_id: int
    boxes: dict[int, Box] = field(default_factory=dict)
    embeddings: list[np.ndarray] = field(default_factory=list)


@dataclass
class Camera:
    id: str
    file: str
    width: int
    height: int
    frame_count: int
    tracks: list[Track]


def box_overlap(box: Box, other: Box) -> int:
    return max(0, min(box[2], other[2]) - max(box[0], other[0])) * max(
        0, min(box[3], other[3]) - max(box[1], other[1])
    )


def track_video(camera_id, video: Path, weights: Path, encoder, fps, image_size):
    from ultralytics import YOLO

    # Each camera must start with fresh ByteTrack state and its own local IDs.
    detector = YOLO(str(weights), task="detect")
    predictions = detector.track(
        source=str(video),
        stream=True,
        tracker="bytetrack.yaml",
        classes=[0],
        conf=0.1,
        imgsz=image_size,
        device="intel:cpu",
        verbose=False,
    )

    tracks = {}
    last_sample = {}
    sample_interval = max(1, round(fps / 3))
    frame_count = 0
    try:
        for frame, result in enumerate(predictions):
            frame_count = frame + 1
            height, width = result.orig_shape
            if frame_count % 250 == 0:
                print(f"  {camera_id}: {frame_count} frames", flush=True)
            if result.boxes.id is None:
                continue

            coordinates = result.boxes.xyxy.cpu().numpy().round().astype(int)
            coordinates = np.clip(coordinates, 0, [width, height, width, height])
            ids = result.boxes.id.int().cpu().tolist()
            scores = result.boxes.conf.cpu().tolist()
            detections = [(local_id, tuple(map(int, box)), score)
                          for local_id, box, score in zip(ids, coordinates, scores)
                          if box[2] > box[0] and box[3] > box[1]]

            for local_id, box, score in detections:
                if local_id not in tracks:
                    tracks[local_id] = Track(camera_id, local_id)
                track = tracks[local_id]
                track.boxes[frame] = box
                left, top, right, bottom = box
                area = (right - left) * (bottom - top)
                if (score < 0.30 or bottom - top < 32
                        or frame - last_sample.get(local_id, -sample_interval) < sample_interval):
                    continue
                if any(box_overlap(box, other) > area * 0.35
                       for other_id, other, _ in detections if local_id != other_id):
                    continue
                embedding = encoder(result.orig_img[top:bottom, left:right])
                if embedding is not None:
                    track.embeddings.append(embedding)
                    last_sample[local_id] = frame
    finally:
        predictions.close()

    if frame_count == 0:
        raise ValueError(f"{camera_id}: no video frames could be decoded")
    minimum_frames = max(2, round(fps * 0.2))
    usable_tracks = [track for track in tracks.values() if len(track.boxes) >= minimum_frames]
    return Camera(camera_id, video.name, width, height, frame_count, usable_tracks)
