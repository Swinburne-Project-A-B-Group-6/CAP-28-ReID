# CAP-28
## Real-Time Person Re-Identification and Tracking on Edge Devices

**Project Category:** Research, Industry  
**Location:** Hanoi

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
