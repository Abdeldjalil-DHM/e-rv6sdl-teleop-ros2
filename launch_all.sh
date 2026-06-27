#!/bin/bash
source ~/ros2_ws/install/setup.bash

echo "🚀 Lancement PFC RV-6SDL..."

# Terminal 1 — Robot URDF + joint_state_publisher_gui
gnome-terminal --title="🤖 Robot URDF" -- bash -c "cd ~/ros2_ws && source install/setup.bash && ros2 launch rv6sdl_description rv6sdl.launch.py; exec bash"

# Terminal 2 — RViz2
gnome-terminal --title="🔵 RViz2" -- bash -c "cd ~/ros2_ws && source install/setup.bash && ros2 run rviz2 rviz2; exec bash"

# Terminal 3 — Rosbridge
gnome-terminal --title="🌐 Rosbridge :9090" -- bash -c "source /opt/ros/jazzy/setup.bash && ros2 launch rosbridge_server rosbridge_websocket_launch.xml; exec bash"

# Terminal 4 — Teleop Node (Phase 2)
gnome-terminal --title="🎮 Teleop Node" -- bash -c "cd ~/ros2_ws && source install/setup.bash && ros2 run rv6sdl_teleop teleop_node; exec bash"

# Attendre que Rosbridge démarre
sleep 4

# Dashboard Chrome
google-chrome ~/Downloads/rv6sdl_dashboard.html

echo "✅ Tout est lancé !"
