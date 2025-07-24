#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")
cd "$PROJECT_ROOT" || exit 1

# Check for Python3 and ensure it's available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3 to use this script."
    exit 1
fi

# Check for openshift-install and ensure it's available
if ! command -v openshift-install &> /dev/null; then
    echo "OpenShift Install could not be found. Please install OpenShift Install to use this script."
    exit 1
fi

# Check for the data path
if [ ! -d "./gui-data" ]; then
    echo "Creating gui-data directory..."
    mkdir -p ./gui-data/{data,graph}
    chmod 777 -R ./gui-data
fi

python3 -m venv ./venv
source ${PROJECT_ROOT}/venv/bin/activate
python3 -m pip install -r ./setup/requirements.txt

export GUI_MODE=${1:-"appliance"} # appliance, agent
export BUILD_BASE_PATH=${BUILD_BASE_PATH:-"${PROJECT_ROOT}/gui-data/data"}
export APPLIANCE_IMAGE=${APPLIANCE_IMAGE:-"quay.io/edge-infrastructure/openshift-appliance@sha256:2a1187cdde61679e87e770c92efff997d02abc6d95bd1a61d6636d5859e83e27"}

cd ${PROJECT_ROOT}/src || exit 1

# Switch between appliance and agent mode
if [ "$GUI_MODE" == "agent" ]; then
    echo "===== Running in agent mode..."
    streamlit run ${PROJECT_ROOT}/src/agent-ui.py
fi

if [ "$GUI_MODE" == "appliance" ]; then
    echo "===== Running in appliance mode..."
    streamlit run ${PROJECT_ROOT}/src/ui.py
fi