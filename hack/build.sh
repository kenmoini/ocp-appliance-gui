#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")
cd "$PROJECT_ROOT" || exit 1

if ! command -v podman &> /dev/null; then
    echo "Podman could not be found. Please install Podman to use this script."
    exit 1
fi

if [ ! -z "$1" ]; then
    export CFILE="$1"
else
    export CFILE="default"
fi

if [ "$CFILE" == "default" ]; then
    echo "Using default Containerfile file: $CFILE"
    podman build -t ocp-appliance-gui .
else
    echo "Using custom configuration file: $CFILE"
    podman build -t ocp-appliance-gui -f "$CFILE" .
fi
