#!/bin/bash

# Update package list
sudo apt update

# add repository
sudo cd /boot/firmware
sudo curl -L -o repo.zip "https://drive.google.com/uc?export=download&id=1UlyohbbRbeYMKxXikM5tmTvr1KySMSpT"
sudo unzip repo.zip

# Copy service files
sudo cp /boot/firmware/Skyhound/*.service /etc/systemd/system/

# Install python3 dependencies
sudo apt update
sudo apt install -y python3-websockets python3-requests python3-pil python3-gpiozero python3-rpi.gpio python3-luma.core python3-luma.lcd


# Reboot the system
sudo reboot
