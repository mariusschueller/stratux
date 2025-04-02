#!/bin/bash -e

# Create the target directory in /boot/firmware
mkdir -p "${ROOTFS_DIR}/boot/firmware/Skyhound"

# Copy files from your stage's data directory to /boot/firmware/Skyhound
cp -r "${STAGE_DIR}/10-stratux/data/"* "${ROOTFS_DIR}/boot/firmware/Skyhound/"

# Set permissions (not critical for FAT32, but useful for consistency)
chmod 755 "${ROOTFS_DIR}/boot/firmware/Skyhound"