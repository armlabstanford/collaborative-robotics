#!/bin/bash

# Update package list
sudo apt update

# Install dependencies
sudo apt install -y portaudio19-dev

# Install Python packages
pip install sounddevice google-cloud-speech google-generativeai
