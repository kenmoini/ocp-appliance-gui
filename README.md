# OpenShift Appliance Installation GUI

## Development/Running

```bash
# Run on an entitled RHEL system
dnf install git podman python3 python3-pip wget -y

git clone https://github.com/kenmoini/ocp-appliance-gui.git
cd ocp-appliance-gui

# One-time: Install OCP binaries
cd setup
./download-ocp-binaries.sh
cd bin
mv * /usr/local/bin
cd ../..

# Setup Python
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

# Run the Appliance UI
streamlit run ui.py

# Run the Agent UI
streamlit run agent-ui.py

# Terminate the venv
deactivate
```

## Container Stuffs

> So evidently Podman-in-Podman-in-Podman is tough?  Appliance GUI doesn't work

```bash
podman build -t ocp-appliance-gui .

podman tag ocp-app-gui quay.io/kenmoini/ocp-appliance-gui:latest

podman push quay.io/kenmoini/ocp-appliance-gui:latest

mkdir -p ./gui-data/{data,graph}
chmod 777 ./gui-data

# Appliance GUI
podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data/data:/data \
 -v ./gui-data/graph:/var/lib/containers \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 ocp-appliance-gui

# Agent GUI
podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data/data:/data \
 -v ./gui-data/graph:/var/lib/containers \
 -e GUI_MODE=agent \
 --net=host \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 ocp-appliance-gui

# Upstream Appliance GUI
podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data/data:/data \
 -v ./gui-data/graph:/var/lib/containers \
 --net=host \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 quay.io/kenmoini/ocp-appliance-gui:latest

# Combo Wombo
podman build -t ocp-appliance-gui . \
 && podman run --name ocp-gui --rm -it -p 8501:8501 \
 -v ./gui-data/data:/data \
 -v ./gui-data/graph:/var/lib/containers \
 --privileged -v /run/podman/podman.sock:/run/podman/podman.sock \
 ocp-appliance-gui
```