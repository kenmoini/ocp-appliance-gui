# OpenShift Appliance Installation GUI

## Development

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

streamlit run ui.py

deactivate
```

## Container Stuffs

```bash
podman build -t ocp-appliance-gui .

podman tag ocp-app-gui quay.io/kenmoini/ocp-appliance-gui:latest

podman push quay.io/kenmoini/ocp-appliance-gui:latest

mkdir -p ./gui-data/
chmod 777 ./gui-data

# Appliance GUI
podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data:/data \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 ocp-appliance-gui

# Agent GUI
podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data:/data \
 -e GUI_MODE=agent \
 --net=host \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 ocp-appliance-gui

# Upstream Appliance GUI
podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data:/data \
 --net=host \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 quay.io/kenmoini/ocp-appliance-gui:latest

# Combo Wombo
podman build -t ocp-appliance-gui . \
 && podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data:/data \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 ocp-appliance-gui
```