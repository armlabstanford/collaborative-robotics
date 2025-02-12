FROM tiryoh/ros2-desktop-vnc:humble

RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    build-essential \
    curl \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update

# Install Python 3.10 and pip
# RUN apt-get install -y python3.10 python3.10-distutils

# # Update alternatives to make Python 3.10 the default
# RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
#     && update-alternatives --set python3 /usr/bin/python3.10

# # Install pip for Python 3.10 
# RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3


RUN sudo apt-get update && sudo apt-get install -yq lsb-release

RUN mkdir -p /dev_ws/src && cd /dev_ws/src \
	&& sudo rm -rf /etc/ros/rosdep/sources.list.d/20-default.list \
	&& sudo rosdep init \
	&& rosdep update --include-eol-distros \
	&& sudo apt-get install -yq ros-humble-rtabmap-ros \
	&& git clone https://github.com/Interbotix/interbotix_ros_core.git -b galactic --recurse-submodules \
	&& git clone https://github.com/Interbotix/interbotix_ros_rovers.git -b humble \
	&& git clone https://github.com/Interbotix/interbotix_ros_toolboxes.git -b humble \
	&& git clone https://github.com/ros-planning/moveit_visual_tools.git -b ros2 \
	&& cd .. && rosdep install --from-paths src --ignore-src --rosdistro humble -r -y


# example: installing ros2 package
# RUN sudo apt-get install -y ros-$ROS_DISTRO-<package-name>

RUN cd /dev_ws && source /opt/ros/humble/setup.bash && colcon build

RUN sudo apt install ros-humble-irobot-create-description
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

