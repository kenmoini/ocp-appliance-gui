#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")

# Check for Python3 and ensure it's available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3 to use this script."
    exit 1
fi


# Check for the data path
if [ ! -d "${PROJECT_ROOT}/gui-data" ]; then
    echo "Creating gui-data directory..."
    mkdir -p ${PROJECT_ROOT}/gui-data/{data,graph}
    chmod 777 -R ${PROJECT_ROOT}/gui-data
fi

python3 -m venv ${PROJECT_ROOT}/gui-data/venv
source ${PROJECT_ROOT}/gui-data/venv/bin/activate
python3 -m pip install -r ${PROJECT_ROOT}/setup/requirements.txt

export GUI_MODE=${1:-"appliance"} # appliance, agent
export BUILD_BASE_PATH=${BUILD_BASE_PATH:-"./gui-data/data"}

# Switch between appliance and agent mode
if [ "$GUI_MODE" == "agent" ]; then
    echo "===== Running in agent mode..."
    streamlit run ${PROJECT_ROOT}/src/agent-ui.py
fi

if [ "$GUI_MODE" == "appliance" ]; then
    echo "===== Running in appliance mode..."
    streamlit run ${PROJECT_ROOT}/src/ui.py
fi