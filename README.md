# CAP-28
## Real-Time Person Re-Identification and Tracking on Edge Devices

**Project Category:** Research, Industry  
**Location:** Hanoi

## Run Re-ID on synchronized recordings

The `AI/` pipeline takes the synchronized clips from one session. It uses
YOLO11n to detect people, ByteTrack to assign local IDs in each camera, and
OpenVINO's `person-reidentification-retail-0277` model to compare appearance
across cameras. It writes browser-ready MP4 files and a separate tracking JSON
with camera metadata and per-frame bounding boxes by Global ID.

From the repository root, set up the CPU environment in PowerShell with Python 3.10.

```powershell
python -m venv AI/.venv
$python = 'AI/.venv/Scripts/python.exe'
& $python -m pip install --upgrade pip
& $python -m pip install torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
& $python -m pip install -r AI/requirements.txt
```

Run the pipeline once with all three recordings. The first run downloads the
model weights to `AI/models/` and exports the detector to OpenVINO for CPU runs.
The videos should start at the same time and have
the same duration. The pipeline transcodes them to 12 FPS by default.

```powershell
& $python AI/run_reid.py `
  --camera 'CAM-01=D:/videos/cam1.mp4' `
  --camera 'CAM-02=D:/videos/cam2.mp4' `
  --camera 'CAM-03=D:/videos/cam3.mp4' `
  --output AI/output/my-session
```

The command saves the videos to `AI/output/my-session/` and the tracking data
to `AI/output/my-session.json`. Use `--tracking` to specify a different JSON path.

Start the local dashboard with `npm.cmd --prefix frontend run dev` after installing
the frontend and AI dependencies. Click **Open video folder** and choose the
folder with synchronized camera videos. The dashboard runs the AI pipeline,
plays the converted MP4s, and replaces `frontend/public/tracking.json` after a
successful run. It assigns camera IDs in filename order. On a failed run it
keeps the last successful tracking file. The local server is required for
processing, including when testing a build with `npm.cmd --prefix frontend run preview`.

The default Re-ID model and threshold are a baseline. Similar clothing and long occlusions
can cause incorrect matches or split a person into multiple Global IDs.

---

## 1. Project Overview

Person re-identification (Re-ID) and multi-object tracking are key
technologies for intelligent surveillance, smart buildings, retail
analytics, and security systems.

The goal is not only to track individuals within a camera view, but also
to recognize the same person across different cameras despite changes
in viewpoint, illumination, pose, and occlusion.

Deploying such systems in real time on resource-constrained edge
devices remains challenging.

CAP-28 aims to develop a real-time person tracking and re-identification
system that runs primarily on edge devices, such as the
Qualcomm–Arduino platform or other embedded hardware.

---

## 2. Project Goals

### Industry Goal

Develop a complete working system for real-time person tracking and
cross-camera person re-identification.

### Research Goal

Investigate approaches to make the Re-ID and tracking pipeline lighter
or faster on Qualcomm edge hardware.

---

## 3. Proposed System

The system is expected to:

- Detect people in video streams.
- Maintain individual identities within each camera using multi-object tracking.
- Extract compact visual embeddings.
- Associate identities across different cameras.
- Operate primarily on edge devices.
- Support communication between multiple devices.
- Provide visualization and system monitoring.

---

## 4. AI Component

The AI component may investigate:

- Lightweight person detectors.
- Multi-object tracking approaches such as ByteTrack or DeepSORT-style methods.
- Metric-learning-based person Re-ID models.
- Efficient embedding architectures.

Potential research directions include:

- Knowledge distillation.
- Quantization.
- Pruning.
- Embedding compression.
- Joint optimization of tracking and Re-ID.

---

## 5. IoT Component

The IoT component will integrate:

- Cameras.
- Edge hardware.
- Communication between multiple devices.

The final communication architecture and hardware selection
will be determined by the project team.

---

## 6. Software Engineering Component

The Software Engineering component will develop:

- Real-time processing pipeline.
- Identity database.
- Communication services.
- Visualization dashboard.
- System monitoring.

Specific technologies and system architecture will be determined
during project development.

---

## 7. Target Evaluation

The system should be evaluated in terms of both recognition/tracking
performance and edge-computing efficiency.

### Recognition and Tracking Metrics

- Rank-1 accuracy.
- mAP.
- IDF1.
- HOTA.

### Edge Performance Metrics

- FPS.
- Latency.
- Memory usage.
- Model size.
- Power consumption.

---

## 8. Expected Outcome

The final outcome should be a working prototype demonstrating:

- Real-time person tracking.
- Cross-camera person re-identification.
- Deployment primarily on edge devices.
- Analysis of the trade-off between recognition accuracy
  and edge-computing efficiency.

---

## 9. Project Development

This repository is used for collaborative development,
research, implementation, documentation, and progress tracking.

Detailed system architecture, technology selection, hardware,
team responsibilities, implementation plans, experiments,
and other project decisions will be added as the team discusses
and finalizes them.

---

## 10. Project Status

**Status:** Initial Setup

- GitHub repository created.
- Project requirements documented.
- Detailed technical design: To be discussed.
- Hardware selection: To be discussed.
- AI model selection: To be discussed.
- System architecture: To be discussed.
- Team task allocation: To be discussed.

---

## 11. Team

Team members, roles, and responsibilities will be updated
after team discussion.

---

## 12. Documentation

Project documentation will be added progressively as the project develops.
