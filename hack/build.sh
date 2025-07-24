#!/bin/bash


if ! command -v podman &> /dev/null; then
    echo "Podman could not be found. Please install Podman to use this script."
    exit 1
fi

podman build -t ocp-appliance-gui .