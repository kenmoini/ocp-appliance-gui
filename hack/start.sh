#!/bin/bash

# Check for podman and ensure it's available
if ! command -v podman &> /dev/null; then
    echo "Podman could not be found. Please install Podman to use this script."
    exit 1
fi

# Check for the data path
if [ ! -d "./gui-data" ]; then
    echo "Creating gui-data directory..."
    mkdir -p ./gui-data/{data,graph}
    chmod 777 -R ./gui-data
fi

export GUI_MODE=${1:-"appliance"} # appliance, agent
export IMAGE_NAME=${IMAGE_NAME:-"ocp-appliance-gui"}

  #-p 8501:8501 \
podman run --name ocp-gui \
  --rm -it \
  --privileged \
  --net=host \
  --security-opt label=disable \
  --device=/dev/fuse \
  -e GUI_MODE=${GUI_MODE} \
  -v ./gui-data/data:/data:Z \
  -v ./gui-data/graph:/var/lib/containers \
  -v /run/podman/podman.sock:/run/podman/podman.sock \
  ${IMAGE_NAME}