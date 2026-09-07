# AMAR — Autonomous Medical Assistance Rover

> **AMAR (Autonomous Medical Assistance Rover)** is a ROS 2–based rover project that combines autonomous navigation, robot simulation, perception, and biomedical signal processing to explore how a mobile robot can reach a person and perform a preliminary bio-scan.

## Project Overview

AMAR is designed as a modular robotic platform for scenarios where a rover may need to navigate an environment, locate or approach a target, and process physiological sensor data.

The current repository contains:

- A ROS 2 robot description based on a TurtleBot3 Burger-style platform with a camera/sensor setup.
- Gazebo / Gazebo Sim environments and rover models for simulation.
- SLAM and Nav2 launch configuration for autonomous navigation.
- A biomedical signal-processing prototype that demonstrates ECG sampling, frequency analysis, filtering, windowing, heart-rate estimation, and artifact detection.
- Separate ROS 2 packages reserved for description, navigation, perception, and signal processing so the system can be extended into a complete integrated rover stack.

> **Current MVP:** the biomedical signal-processing pipeline is implemented as a standalone Python simulation using a real ECG dataset. The ROS 2 navigation and simulation stack provides the robotic foundation for integrating this bio-scan pipeline with the rover.

---

## Key Features

### 1. Autonomous Rover Simulation

AMAR can be simulated in Gazebo Sim using a TurtleBot3-based rover model.

The simulation package includes:

- TurtleBot3 Burger camera model
- Custom SDF/URDF/Xacro robot descriptions
- Gazebo worlds
- Sensor and mesh assets
- ROS–Gazebo bridges
- RViz2 visualization
- SLAM Toolbox integration
- Nav2 navigation configuration

### 2. Navigation and SLAM

The project includes a launch configuration that brings together:

**Gazebo → ROS-Gazebo Bridge → SLAM Toolbox → Nav2 → RViz2**

This provides the foundation for mapping an environment and performing autonomous navigation.

### 3. Biomedical Signal Processing

The `AMAR-bsp-sim` module demonstrates the rover's proposed bio-scan workflow using a real ECG recording.

The pipeline consists of four stages:

1. **Sampling & Aliasing**  
   Demonstrates why an appropriate sampling rate is necessary for accurately capturing a physiological signal.

2. **Frequency Analysis**  
   Uses Welch's Power Spectral Density method to identify dominant frequency components associated with the heartbeat.

3. **Digital Filtering**  
   Applies a 4th-order Butterworth band-pass filter from **0.5–40 Hz** and zero-phase filtering using `filtfilt` to reduce unwanted signal components while preserving timing.

4. **Windowing & Artifact Detection**  
   Splits the signal into **10-second windows**, detects ECG R-peaks, estimates heart rate, and flags unreliable windows.

### 4. Scan Report Generation

Running the biomedical signal-processing pipeline automatically generates:

- Sampling visualization
- Frequency-domain visualization
- Before/after filtering visualization
- Heart-rate-over-time visualization
- A text-based scan report

---

## System Architecture

```text
                     ┌──────────────────────┐
                     │      AMAR Rover      │
                     └──────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       ┌────────────┐    ┌────────────┐    ┌──────────────┐
       │ Perception │    │ Navigation │    │ Bio-Scanner  │
       │   Camera   │    │ SLAM/Nav2  │    │ ECG / PPG /  │
       │   Sensors  │    │            │    │ Respiration  │
       └─────┬──────┘    └─────┬──────┘    └──────┬───────┘
             │                 │                  │
             ▼                 ▼                  ▼
       ┌────────────────────────────────────────────────┐
       │                    ROS 2                       │
       │  Robot Description │ Navigation │ Data Topics  │
       └────────────────────────┬───────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Gazebo / RViz2  │
                       │   Simulation    │
                       └─────────────────┘

Bio-Scan Processing:

Raw ECG
   │
   ▼
Sampling / Aliasing Demo
   │
   ▼
Frequency Analysis (Welch PSD)
   │
   ▼
Band-pass Filtering (0.5–40 Hz)
   │
   ▼
10-second Windowing
   │
   ▼
R-Peak Detection
   │
   ▼
Heart Rate + Artifact Detection
   │
   ▼
Scan Report
```

---

## Repository Structure

```text
AMAR-BM-INNO-Project-master/
│
├── README.md
│
├── AMAR-bsp-sim/
│   ├── rover_bsp_sim.py
│   ├── requirements.txt
│   ├── README.md
│   ├── docs/
│   │   └── explanation.md
│   └── outputs/
│       ├── 1_sampling.png
│       ├── 2_frequency.png
│       ├── 3_filtering.png
│       ├── 4_windowed_hr.png
│       └── scan_report.txt
│
└── src/
    │
    ├── amar_description/
    │   ├── urdf/
    │   ├── meshes/
    │   ├── models/
    │   ├── rviz/
    │   └── launch/
    │
    ├── amar_navigation/
    │
    ├── amar_perception/
    │
    ├── amar_signalprocessing/
    │
    └── amar_simulation/
        ├── launch/
        ├── models/
        ├── params/
        └── worlds/
```

---

# Getting Started

## Prerequisites

The ROS 2 portion of the project requires a Linux environment with:

- ROS 2
- Python 3
- Gazebo Sim / ROS-Gazebo integration
- RViz2
- Nav2
- SLAM Toolbox
- `xacro`
- `joint_state_publisher`

The biomedical signal-processing module requires:

- Python 3
- NumPy
- SciPy
- Matplotlib
- NeuroKit2
- Pandas

> The exact ROS 2 distribution and Gazebo version should match the environment used by your team. The launch files use ROS 2 packages such as `nav2_bringup`, `slam_toolbox`, `ros_gz_sim`, `ros_gz_bridge`, and `ros_gz_image`.

---

# Running the Biomedical Signal-Processing MVP

Navigate to the BSP simulation directory:

```bash
cd AMAR-bsp-sim
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python3 rover_bsp_sim.py
```

On the first run, NeuroKit2 downloads the sample dataset:

`bio_resting_5min_100hz`

The dataset is a real 5-minute resting-state recording sampled at **100 Hz**, containing ECG, PPG, and respiration channels. The current pipeline uses the ECG channel.

---

## BSP Output

After execution, the `outputs/` directory contains:

| Output | Description |
|---|---|
| `1_sampling.png` | Correct sampling compared with an under-sampled ECG signal |
| `2_frequency.png` | Frequency-domain representation using Welch's method |
| `3_filtering.png` | Raw ECG compared with the filtered signal |
| `4_windowed_hr.png` | Heart rate estimated for each 10-second window |
| `scan_report.txt` | Summary of frequency, heart rate, frames, and detected bad frames |

### Example Processing Flow

```text
Real ECG Dataset
      │
      ▼
100 Hz Sampling
      │
      ├──► Aliasing demonstration
      │
      ▼
Welch Frequency Analysis
      │
      ▼
0.5–40 Hz Butterworth Band-pass
      │
      ▼
10-second Windows
      │
      ▼
ECG R-Peak Detection
      │
      ▼
Heart Rate Estimation
      │
      ▼
Artifact / Bad-frame Detection
      │
      ▼
Scan Report
```

---

# Running the ROS 2 Simulation

From the project root, create a ROS 2 workspace if required:

```bash
mkdir -p ~/amar_ws/src
```

Copy or clone the repository into the workspace's `src` directory.

Then build:

```bash
cd ~/amar_ws
source /opt/ros/<ros2-distro>/setup.bash
colcon build
source install/setup.bash
```

## Launch the Robot Description

```bash
ros2 launch amar_description robot_state_publisher.launch.py
```

This loads the robot's Xacro description, publishes its state, and opens RViz2 using the project's configuration.

## Launch a Gazebo World

For the standard TurtleBot3 world:

```bash
ros2 launch amar_simulation turtlebot3_world.launch.py
```

For the house environment:

```bash
ros2 launch amar_simulation turtlebot3_house.launch.py
```

## Spawn the Rover

```bash
ros2 launch amar_simulation spawn_turtlebot3.launch.py
```

The spawn launch file also starts the ROS-Gazebo bridge and camera image bridge.

## Launch SLAM + Nav2

```bash
ros2 launch amar_simulation slam_nav2.launch.py
```

This starts:

- Nav2 navigation
- SLAM Toolbox
- RViz2

with simulation time enabled.

> Depending on the ROS 2/Gazebo installation, additional system dependencies or configuration may be required before these launch files run successfully.

---

# Technology Stack

| Technology | Purpose |
|---|---|
| **ROS 2** | Robot middleware and communication |
| **Python** | Processing and ROS 2 launch/configuration |
| **Gazebo Sim** | Rover and environment simulation |
| **RViz2** | Visualization and monitoring |
| **Nav2** | Autonomous navigation |
| **SLAM Toolbox** | Mapping and localization |
| **OpenCV / Camera stack** | Planned/extendable perception pipeline |
| **NumPy** | Numerical computation |
| **SciPy** | Digital signal processing |
| **NeuroKit2** | Biomedical signal processing and ECG peak detection |
| **Matplotlib** | Signal visualization |
| **Pandas** | Biomedical dataset handling |
| **Linux** | Primary robotics development environment |

---

# Biomedical Signal Processing Details

## Sampling

The reference dataset is sampled at:

```text
FS = 100 Hz
```

The project intentionally reduces a 3-second ECG segment to an effective sampling rate of:

```text
100 / 8 = 12.5 Hz
```

This demonstrates **aliasing**, where insufficient sampling causes the recorded signal to become distorted.

## Frequency Analysis

Welch's method is used to estimate the Power Spectral Density:

```python
freqs, psd = scipy.signal.welch(ecg_raw, fs=100, nperseg=1024)
```

The dominant frequency is searched within:

```text
0.7–2.0 Hz
```

which corresponds approximately to:

```text
42–120 BPM
```

This restricted range helps prevent a harmonic of the ECG waveform from being incorrectly interpreted as the fundamental heart rate.

## Filtering

The ECG is processed using a 4th-order Butterworth band-pass filter:

```text
0.5 Hz ≤ signal ≤ 40 Hz
```

`filtfilt()` is used for zero-phase filtering so that the timing of ECG peaks is not shifted before heart-rate measurement.

## Windowing

The filtered ECG is divided into:

```text
10-second windows
```

R-peaks are detected using NeuroKit2. Consecutive R-peaks provide RR intervals, from which heart rate is calculated:

```text
Heart Rate (BPM) = 60 / mean(RR interval in seconds)
```

Frames are flagged when:

- fewer than two R-peaks are detected,
- peak detection fails, or
- the estimated heart rate falls outside the configured 40–180 BPM sanity range.

---

# Project Status

### Implemented

- [x] ROS 2 package structure
- [x] Rover URDF/Xacro and mesh assets
- [x] Gazebo Sim rover model
- [x] Gazebo world environments
- [x] ROS-Gazebo bridges
- [x] RViz2 configuration
- [x] SLAM Toolbox + Nav2 launch integration
- [x] Real ECG dataset integration
- [x] Sampling / aliasing demonstration
- [x] Frequency-domain analysis
- [x] ECG filtering
- [x] Window-based heart-rate estimation
- [x] Basic artifact detection
- [x] Automatic scan report generation

### Planned / Extendable

- [ ] Integrate the bio-scan pipeline directly with live rover sensor topics
- [ ] Add physical biomedical sensors
- [ ] Implement a complete ROS 2 perception node
- [ ] Fuse camera perception with navigation
- [ ] Add real-time health-status estimation
- [ ] Add HRV metrics such as SDNN and RMSSD
- [ ] Improve artifact detection using RR-interval consistency
- [ ] Add overlapping analysis windows
- [ ] Test ECG, PPG, and respiration streams together
- [ ] Deploy and validate the complete pipeline on the physical rover

---

# Future Vision

The long-term goal of AMAR is to move from a simulated rover and offline biomedical dataset toward a **real-time autonomous medical-assistance platform**.

A future end-to-end workflow could look like:

```text
Environment
    │
    ▼
Autonomous Navigation
    │
    ▼
Target / Person Detection
    │
    ▼
Approach & Positioning
    │
    ▼
Biomedical Sensor Acquisition
    │
    ▼
Signal Processing
    │
    ▼
Vital-Sign Extraction
    │
    ▼
Quality / Artifact Check
    │
    ▼
Health Information for the Operator
```

The system is intended as a **prototype and research/engineering platform**, not as a medical diagnostic device.

---

# Contributing

Contributions are welcome.

A typical workflow is:

```bash
git checkout -b feature/your-feature
# make your changes
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

Then open a pull request for review.

---

# License

This repository currently contains package metadata with placeholder license fields. Before public release, the project should declare an explicit project license and verify the licenses of third-party assets and models included in the repository.

Some simulation assets are derived from or based on TurtleBot3 / Open Robotics resources and retain their respective license notices.

---

# Acknowledgements

- **ROS 2** for the robotics middleware ecosystem.
- **Nav2** for autonomous navigation.
- **SLAM Toolbox** for mapping and localization.
- **Gazebo Sim** for robot simulation.
- **TurtleBot3 / ROBOTIS** for the base robot model and simulation resources.
- **NeuroKit2** for biomedical signal-processing utilities and the reference ECG dataset.
- **NumPy, SciPy, Pandas, and Matplotlib** for numerical analysis and visualization.

---

## Authors:
* **Bhagabanta Giri** *B.Tech, Biomedical Engineering* **NIT Rourkela**
* **Meghna Vijesh** *B.Tech, Biomedical Engineering* **NIT Rourkela**
* **Satyam Kalapahad** *B.Tech, Biomedical Engineering* **NIT Rourkela**
* **Riyana P A** *B.Tech, Biomedical Engineering* **NIT Rourkela**
* **Sai Arpit Dash** *B.Tech, Biomedical Engineering* **NIT Rourkela**

---

## AMAR

**Autonomous Medical Assistance Rover**

*Navigate. Perceive. Scan. Assist.*
