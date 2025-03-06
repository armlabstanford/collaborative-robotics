FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Set up environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="${PATH}:/home/user/.local/bin"

# We love UTF!
ENV LANG C.UTF-8

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Set the nvidia container runtime environment variables
ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics
ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV CUDA_HOME="/usr/local/cuda"
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6+PTX 8.9"

RUN apt-get update && apt-get install -y \
    build-essential \
    mesa-utils \
    libgl1-mesa-glx \
    libglu1-mesa \
    xorg \
    wget && \
    rm -rf /var/lib/apt/lists/*

# Set up OpenGL test application (optional)
RUN apt-get update && apt-get install -y mesa-utils && rm -rf /var/lib/apt/lists/*


RUN set -x \
	&& apt-get update \
	&& apt-get install -y apt-transport-https ca-certificates \
	&& apt-get install -y git vim tmux nano htop sudo curl wget gnupg2 \
	&& apt-get install -y bash-completion \
	&& rm -rf /var/lib/apt/lists/* \
	&& useradd -ms /bin/bash user \
	&& echo "user:user" | chpasswd && adduser user sudo \
	&& echo "user ALL=(ALL) NOPASSWD: ALL " >> /etc/sudoers

# RUN install ikpy
RUN apt-get update && apt-get install -y python3-pip

SHELL ["/bin/bash", "-c"]

RUN set -x \
    && apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.9 python3.9-venv python3.9-dev \
    && apt-get install -y python3.11-tk

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 2


RUN set -x \
    && apt install -y software-properties-common && add-apt-repository universe \
    && apt-get update \
    && apt update && apt install curl -y \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && apt update && apt install -y ros-humble-desktop



# do the git clone of dynamixel sdk
RUN apt-get install -y git
RUN source /opt/ros/humble/setup.bash && echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc


RUN apt-get update && apt install -y ros-humble-xacro

RUN apt install -y ros-humble-joint-state-publisher && apt install -y ros-humble-joint-state-publisher-gui

RUN sh -c 'echo "deb [arch=amd64,arm64] http://repo.ros2.org/ubuntu/main `lsb_release -cs` main" > /etc/apt/sources.list.d/ros2-latest.list' \
    && curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc |  apt-key add - \
    && apt update && apt install -y python3-colcon-common-extensions

WORKDIR /home/user

ENV LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"

RUN sudo pip uninstall numpy -y && pip install numpy==1.26.4 && pip install pygame && pip install zarr && pip install tqdm 

RUN apt install -y ninja-build

RUN pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121