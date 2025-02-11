FROM peasant98/vnc-galactic:latest

RUN sudo apt-get update && sudo apt-get install -yq lsb-release

RUN mkdir -p /dev_ws/src && cd /dev_ws/src \
	&& sudo rm -rf /etc/ros/rosdep/sources.list.d/20-default.list \
	&& sudo rosdep init \
	&& rosdep update --include-eol-distros \
	&& sudo apt-get install -yq ros-galactic-rtabmap-ros \
	&& git clone https://github.com/Interbotix/interbotix_ros_core.git -b galactic --recurse-submodules \
	&& git clone https://github.com/Interbotix/interbotix_ros_rovers.git -b galactic \
	&& git clone https://github.com/Interbotix/interbotix_ros_toolboxes.git -b galactic \
	&& git clone https://github.com/ros-planning/moveit_visual_tools.git -b ros2 \
	&& cd .. && rosdep install --from-paths src --ignore-src --rosdistro galactic -r -y


# feel free to add to your dockerfile here

# example: installing ros2 package
# RUN sudo apt-get install -y ros-$ROS_DISTRO-<package-name>

RUN cd /dev_ws && source /opt/ros/galactic/setup.bash && colcon build

RUN sudo apt install ros-galactic-irobot-create-description
RUN pip install modern_robotics

RUN sudo apt-get install -y  ros-$ROS_DISTRO-pcl-ros ros-$ROS_DISTRO-pcl-conversions

# install scipy
RUN sudo apt install nano gedit -y

RUN sudo apt install -y \
ros-$ROS_DISTRO-gazebo-ros2-control \
ros-$ROS_DISTRO-gazebo-ros2-control-demos \
ros-$ROS_DISTRO-effort-controllers \
ros-$ROS_DISTRO-joint-state-broadcaster

RUN /usr/bin/python3 -m pip install scipy 

COPY ./entrypoint.sh /
ENTRYPOINT [ "/bin/bash", "-c", "/entrypoint.sh" ]

ENV USER ubuntu
ENV PASSWD ubuntu