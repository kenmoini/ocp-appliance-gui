#!/bin/bash

# Global environment variables
export GUI_MODE=${GUI_MODE:-"appliance"} # appliance, agent
export BUILD_BASE_PATH=${BUILD_BASE_PATH:-"/data/builds"}

# Appliance mode things
#export APPLIANCE_IMAGE=${APPLIANCE_IMAGE:-"quay.io/edge-infrastructure/openshift-appliance:latest"}
export APPLIANCE_IMAGE=${APPLIANCE_IMAGE:-"quay.io/edge-infrastructure/openshift-appliance@sha256:2a1187cdde61679e87e770c92efff997d02abc6d95bd1a61d6636d5859e83e27"}

# Switch between appliance and agent mode
if [ "$GUI_MODE" == "agent" ]; then
    echo "===== Running in agent mode..."
    streamlit run /opt/app-root/src/gui/agent-ui.py
fi

if [ "$GUI_MODE" == "appliance" ]; then
    echo "===== Running in appliance mode..."
    streamlit run /opt/app-root/src/gui/ui.py
fi