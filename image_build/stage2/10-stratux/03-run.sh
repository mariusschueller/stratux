#!/bin/bash -e

# --- Stage 1: Download repository and install dependencies ---

# --- Stage 2: Minimize image size by removing unnecessary packages ---
# NOTE:
#  sed is considered an essential package
#  gcc-12-base is not the compiler but rather the libraries
#  lua5.1 and luajit are required for bluetooth (through a dependency chain)
#  parted is required for bluetooth (through a dependency chain)
#  dos2unix is a dependency of userconf-pi (which is installed by an export stage)

on_chroot << EOF
    apt purge -y cifs-utils
    apt purge -y eject
    apt purge -y gcc g++
    apt purge -y git git-man
    apt purge -y libfontconfig1
    apt purge -y libfreetype6
    apt purge -y gdb
    apt purge -y ntfs-3g
    apt purge -y xauth
    apt purge -y cpp cpp-12
    apt purge -y ed
    apt purge -y libqt5core5a
    apt purge -y libsource-highlight-common libsource-highlight4v5
    apt purge -y libtiff6
    apt purge -y strace
    apt purge -y v4l-utils
    apt purge -y apparmor
    apt purge -y ncdu
    apt purge -y libc6-dev
    apt purge -y pkgconf
    apt purge -y python3-apt
    apt purge -y python3-colorzero
    apt purge -y udisks2
    apt purge -y xkb-data
    apt purge -y m4
    apt purge -y make
    apt purge -y nfs-common
    apt purge -y ppp
    apt purge -y fbset
    apt purge -y manpages
    apt purge -y manpages-dev
    apt purge -y man-db

    apt -y autoremove

    apt update
    
    apt install -y python3-websockets
    apt install -y python3-requests
    apt install -y python3-pil 
    apt install -y python3-gpiozero 
    apt install -y python3-rpi.gpio 
    apt install -y python3-luma.core 
    apt install -y python3-luma.lcd
EOF


mkdir -p "${ROOTFS_DIR}/boot/firmware/Skyhound"

# Copy files from your stage's data directory to /boot/firmware/Skyhound
cp -r "${STAGE_DIR}/10-stratux/data/"* "${ROOTFS_DIR}/boot/firmware/Skyhound/"

# Copy the systemd service files to /etc/systemd/system
cp -r "${ROOTFS_DIR}/boot/firmware/Skyhound/"*.service "${ROOTFS_DIR}/etc/systemd/system/"

# Set permissions (not critical for FAT32, but useful for consistency)
chmod 755 "${ROOTFS_DIR}/boot/firmware/Skyhound"