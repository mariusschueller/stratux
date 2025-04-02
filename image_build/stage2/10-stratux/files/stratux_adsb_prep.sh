#!/usr/bin/bash

if [ ! -d /run/dump1090-mutability ]; then
    mkdir /run/dump1090-mutability
else
    echo "Directory /run/dump1090-mutability already exists."
fi
cp /boot/firmware/skyhound/stratux_wswrite.py /run

