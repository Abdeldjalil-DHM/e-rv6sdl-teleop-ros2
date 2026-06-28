# RV-6SDL Teleoperation and Monitoring over Distributed ROS 2 Jazzy

A distributed robotics project for teleoperation, monitoring, and web-based supervision of the Mitsubishi **RV-6SDL** industrial robot using **ROS 2 Jazzy**, a **Jetson Nano** as the central edge server, and a lightweight **HTML/JavaScript dashboard**.

## Project Overview

This repository contains the implementation of a final-year engineering project focused on building a distributed architecture for industrial robot supervision and remote interaction. The system is designed around a clear separation of roles:

- **Robot layer**: Mitsubishi RV-6SDL with CR2DA controller
- **Edge/server layer**: Jetson Nano running ROS 2 nodes, bridge services, and rosbridge
- **Client layer**: development PC and remote client PCs
- **Web layer**: browser-based dashboard connected through WebSocket

The goal is to provide a scalable and clean architecture for:

- Real-time robot monitoring
- Teleoperation from multiple clients
- ROS 2 integration
- Future deployment of vision and cloud services

## System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                DISTRIBUTED ARCHITECTURE                │
│                                                         │
│  Mitsubishi RV-6SDL + CR2DA Controller                 │
│       │                                                 │
│  Ethernet TCP/IP :10001 (MELFA protocol)               │
│       │                                                 │
│  ┌────▼──────────────────────────────────────────────┐  │
│  │              Jetson Nano (Central Server)         │  │
│  │  - ROS 2 Jazzy nodes                              │  │
│  │  - MELFA socket bridge                            │  │
│  │  - rosbridge_server (:9090)                       │  │
│  │  - Docker containers                              │  │
│  │  - Vision / cloud extensions (future)             │  │
│  └────────────────┬──────────────────────────────────┘  │
│                   │ WebSocket ws://<jetson-ip>:9090     │
│       ┌───────────┴──────────────┐                      │
│       │                          │                      │
│  ┌────▼────┐               ┌─────▼────┐                 │
│  │ Dev PC  │               │ Clients  │                 │
│  │ Ubuntu  │               │ Browser  │                 │
│  │ RViz2   │               │Dashboard │                 │
│  └─────────┘               └──────────┘                 │
└─────────────────────────────────────────────────────────┘
```

## Hardware and Software Stack

### Hardware

- **Robot**: Mitsubishi RV-6SDL-S15, 6 axes, 6 kg payload
- **Controller**: CR2DA-711-S15
- **Edge device**: Jetson Nano
- **Development machine**: ASUS VivoBook X415JA running Ubuntu
- **Clients**: multiple PCs connected through the network

### Software

- **OS**: Ubuntu
- **ROS version**: ROS 2 Jazzy Jalisco
- **Communication**: MELFA TCP/IP over port `10001`
- **Web communication**: `rosbridge_server` on port `9090`
- **Dashboard**: pure HTML/CSS/JavaScript
- **Visualization**: RViz2
- **Containerization**: Docker

## Workspace Structure

This repository is built around the ROS 2 workspace located at:

```bash
~/ros2_ws/
```

### Main packages

- `rv6sdl_description` — URDF model and launch files
- `rv6sdl_interfaces` — custom ROS 2 messages and services
- `rv6sdl_teleop` — teleoperation nodes
- `rv6sdl_monitoring` — monitoring and logging nodes
- `rv6sdl_bringup` — global launch files
- `hello_jazzy` — test package
- `my_first_robot` — test package

### Important files

- `index.html` — GitHub Pages entry point
- `rv6sdl_dashboard.html` — main web dashboard
- `launch_all.sh` — quick project startup script
- `rv6sdl.rviz` — RViz configuration

## Dashboard

The dashboard is a lightweight browser interface designed for monitoring and teleoperation through ROS 2 topics exposed with rosbridge.

### Main ROS 2 topics

| Topic | Type | Direction | Purpose |
|------|------|-----------|---------|
| `/joint_states` | `sensor_msgs/JointState` | Subscribe | Robot joint feedback |
| `/tcp_pose` | `geometry_msgs/Pose` | Subscribe | End-effector pose |
| `/robot_status` | `std_msgs/String` | Subscribe | Robot state and flags |
| `/robot_command` | `std_msgs/String` | Publish | High-level commands |
| `/robot_jog` | `std_msgs/String` | Publish | Jog control |
| `/robot_speed` | `std_msgs/Int32` | Publish | Speed override |

## Current Progress

### Completed

- ROS 2 Jazzy installed and configured
- Workspace compiled successfully
- RV-6SDL URDF loaded in RViz2
- rosbridge WebSocket server operational on port `9090`
- Dashboard connected and receiving live `/joint_states`
- Quick launch workflow prepared
- GitHub Pages deployment configured for public demo access

### Planned next phases

1. **Simulated teleoperation**
   - Simulate HOME / ENABLE / RESET commands
   - Simulate jog control
   - Publish status and TCP pose

2. **CR2DA bridge for the real robot**
   - TCP socket communication with MELFA protocol
   - Read robot state, joint position, and TCP pose
   - Send STOP and speed commands safely

3. **Real robot teleoperation**
   - Real jog and control commands
   - Point-to-point trajectories
   - Safety validation

4. **Distributed deployment on Jetson Nano**
   - Containerized ROS 2 services
   - Multi-client web access
   - Stable edge-server architecture

5. **Advanced dashboard features**
   - Real-time charts
   - Error and status alerts
   - Trajectory recording and CSV export
   - Multi-robot mode

6. **Vision and cloud extensions**
   - USB camera integration
   - YOLO-based object detection
   - Remote monitoring through cloud services

## MELFA TCP/IP Reference

The robot controller communication is based on MELFA commands over a TCP socket:

- **Controller IP**: `192.168.0.1`
- **Jetson IP**: `192.168.0.10`
- **Port**: `10001`

### Example commands

| Command | Description |
|---------|-------------|
| `1;1;JPOSF` | Read joint positions |
| `1;1;PPOSF` | Read TCP position |
| `1;1;STATE` | Read controller state |
| `1;1;STOP` | Emergency stop / stop command |
| `1;1;OVRD=50` | Set speed override to 50% |

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Abdeldjalil-DHM/e-rv6sdl-teleop-ros2.git
cd e-rv6sdl-teleop-ros2
```

### 2. Build the workspace

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### 3. Run the project

```bash
chmod +x launch_all.sh
./launch_all.sh
```

### 4. Open the dashboard

Local development:

```text
ws://localhost:9090
```

Production / Jetson deployment:

```text
ws://<jetson-ip>:9090
```

## GitHub Pages Demo

The public dashboard entry page is available at:

[https://abdeldjalil-dhm.github.io/e-rv6sdl-teleop-ros2/](https://abdeldjalil-dhm.github.io/e-rv6sdl-teleop-ros2/)

## Engineering Goals

This project is not just a local robot demo. It is designed as a distributed robotics platform with the following objectives:

- Separate development, control, and client layers
- Support multi-PC access through a central Jetson Nano server
- Build a web-accessible monitoring and teleoperation interface
- Prepare the system for future AI vision and cloud monitoring extensions
- Keep the architecture modular, scalable, and compatible with industrial workflows

## Author

**Abdeldjalil**  
Final-Bachelor Engineering Project 
USTHB — Algiers, 2026

## License

This repository is intended for academic, research, and demonstration purposes.
