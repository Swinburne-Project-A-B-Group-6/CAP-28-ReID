from itertools import combinations
from pathlib import Path
import cv2
import numpy as np
from openvino import Core
from track_video import Track


class AppearanceEncoder:
    """Create unit-length whole-person embeddings using the OpenVINO retail model."""

    def __init__(self, model: Path, threads: int):
        self.model = Core().compile_model(
            str(model),
            "CPU",
            {"INFERENCE_NUM_THREADS": threads, "PERFORMANCE_HINT": "LATENCY"},
        )
        self.input = self.model.input(0)
        self.output = self.model.output(0)
        _, _, self.height, self.width = self.input.shape
        self.dtype = self.input.element_type.to_dtype()

    def __call__(self, crop):
        resized = cv2.resize(crop, (self.width, self.height))
        tensor = np.ascontiguousarray(resized.transpose(2, 0, 1)[None], dtype=self.dtype)
        vector = self.model([tensor])[self.output].ravel().astype(np.float32)
        magnitude = np.linalg.norm(vector)
        return vector / magnitude if magnitude > 0 else None


def appearance_samples(track: Track):
    if not track.embeddings:
        return None
    # Keep samples from across the whole track when a video is long.
    indices = np.linspace(0, len(track.embeddings) - 1, min(32, len(track.embeddings)), dtype=int)
    return np.stack([track.embeddings[index] for index in indices])


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    scores = a @ b.T
    # Require support looking both ways so a single accidental match has limited influence.
    return float((np.quantile(scores.max(axis=1), 0.65)
                  + np.quantile(scores.max(axis=0), 0.65)) / 2)


def associate(tracks: list[Track], threshold: float) -> dict[tuple[str, int], int]:
    samples = [appearance_samples(track) for track in tracks]
    scores = {}
    conflicts = set()
    candidates = []

    for a, b in combinations(range(len(tracks)), 2):
        first, second = tracks[a], tracks[b]
        same_camera = first.camera_id == second.camera_id
        if same_camera and not first.boxes.keys().isdisjoint(second.boxes):
            conflicts.add((a, b))
            continue
        if samples[a] is None or samples[b] is None:
            continue
        score = scores[a, b] = similarity(samples[a], samples[b])
        required = min(1.0, threshold + 0.05) if same_camera else threshold
        if score >= required:
            candidates.append((score, a, b))

    groups = {index: {index} for index in range(len(tracks))}
    owner = list(groups)
    for _, a, b in sorted(candidates, key=lambda candidate: (-candidate[0], candidate[1], candidate[2])):
        first, second = owner[a], owner[b]
        if first == second:
            continue
        pairs = (tuple(sorted((x, y))) for x in groups[first] for y in groups[second])
        if any(pair in conflicts or scores.get(pair, 1.0) < threshold - 0.12 for pair in pairs):
            continue
        for member in groups.pop(second):
            groups[first].add(member)
            owner[member] = first

    ordered = sorted(groups.values(), key=lambda members: min(
        (min(tracks[i].boxes), tracks[i].camera_id, tracks[i].local_id) for i in members
    ))
    return {
        (tracks[index].camera_id, tracks[index].local_id): global_id
        for global_id, members in enumerate(ordered, 1)
        for index in members
    }
