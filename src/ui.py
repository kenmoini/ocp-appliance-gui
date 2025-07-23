import streamlit as st
from jinja2 import Environment, FileSystemLoader
import os, time, subprocess
#import boto3
#from botocore.exceptions import ClientError

# Setup Jinja2 environment for templating
environment = Environment(loader=FileSystemLoader("templates/"))
applianceConfigTemplate = environment.get_template("appliance-config.yaml.j2")

# Defaults
enableDefaultSources = False
stopLocalRegistry = False
createPinnedImageSets = False
enableInteractiveFlow = False
useDefaultSourceNames = False

availableOperators = {
    "advanced-cluster-management": {"catalog": "redhat", "id": "advanced-cluster-management", "displayName": "ACM"},
    "ansible-automation-platform-operator": {"catalog": "redhat", "id": "ansible-automation-platform-operator", "displayName": "AAP2"},
    "cincinnati-operator": {"catalog": "redhat", "id": "cincinnati-operator", "displayName": "Update Service"},
    "devspaces": {"catalog": "redhat", "id": "devspaces", "displayName": "DevSpace"},
    "devworkspace-operator": {"catalog": "redhat", "id": "devworkspace-operator", "displayName": "DevWorkspace"},
    "rhods-operator": {"catalog": "redhat", "id": "rhods-operator", "displayName": "OpenShift AI"},
    "local-storage-operator": {"catalog": "redhat", "id": "local-storage-operator", "displayName": "LSO"},
    "lvms-operator": {"catalog": "redhat", "id": "lvms-operator", "displayName": "LVMO"},
    "metallb-operator": {"catalog": "redhat", "id": "metallb-operator", "displayName": "MetalLB"},
    "mtv-operator": {"catalog": "redhat", "id": "mtv-operator", "displayName": "Migration Toolkit for Virtualization"},
    "multicluster-engine": {"catalog": "redhat", "id": "multicluster-engine", "displayName": "MCE"},
    "ocs-client-operator": {"catalog": "redhat", "id": "ocs-client-operator", "displayName": "OCS Client"},
    "odf-operator": {"catalog": "redhat", "id": "odf-operator", "displayName": "ODF"},
    "openshift-gitops-operator": {"catalog": "redhat", "id": "openshift-gitops-operator", "displayName": "GitOps"},
    "openshift-pipelines-operator-rh": {"catalog": "redhat", "id": "openshift-pipelines-operator-rh", "displayName": "Pipelines"},
    "redhat-oadp-operator": {"catalog": "redhat", "id": "redhat-oadp-operator", "displayName": "OADP"},
    "rhacs-operator": {"catalog": "redhat", "id": "rhacs-operator", "displayName": "ACS"},
    "kubevirt-hyperconverged": {"catalog": "redhat", "id": "kubevirt-hyperconverged", "displayName": "OpenShift Virtualization"},
    "nfd": {"catalog": "redhat", "id": "nfd", "displayName": "NFD"},
    "fence-agents-remediation": {"catalog": "redhat", "id": "fence-agents-remediation", "displayName": "FAR"},
    "node-maintenance-operator": {"catalog": "redhat", "id": "node-maintenance-operator", "displayName": "NMO"},
}

if "configText" not in st.session_state:
    st.session_state["configText"] = "To be generated..."

# Load CSS
with open('./static/custom.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Page configuration
st.title("OpenShift Appliance Installer")
st.header("Configuration Generator")

with st.sidebar:
    st.markdown("## Helpful Links")
    st.markdown("[Downloads](https://console.redhat.com/openshift/downloads/)")
    st.markdown("[Update Graph](https://access.redhat.com/labs/ocpupgradegraph/update_path/)")
    
col1, col2 =st.columns(2)

with col1:
    ocpVersion = st.selectbox(label="OpenShift Version", 
                                options=["4.18", "4.19"],index=0)
    ocpChannel = st.selectbox(label="OpenShift Channel", 
                                options=["stable"],index=0)
    ocpArchitecture = st.selectbox(label="CPU Architecture", 
                                options=["x86_64","aarch64","ppc64le"],index=0)
with col2:
    coreUserPass = st.text_input(label="core User Password")
    fipsMode = st.selectbox(label="FIPS Mode", 
                                    options=["Disabled", "Enabled"],index=0)

pullSecret = st.text_input(label="OpenShift Pull Secret", type="password")
publicKey = st.text_input(label="SSH Public Key")

operatorOptionNames = [op["displayName"] for op in availableOperators.values()]
includedOperators = st.multiselect(
    "Included Operators",
    operatorOptionNames,
)

submit_button = st.button(label="Generate Configuration")

if submit_button:
    # Validate inputs
    if not pullSecret:
        st.error("Pull Secret is required.")
    else:
        compiledInputData = {
            "ocpVersion": ocpVersion,
            "ocpChannel": ocpChannel,
            "ocpArchitecture": ocpArchitecture,
            "coreUserPass": coreUserPass,
            "fipsMode": fipsMode,
            "pullSecret": pullSecret,
            "publicKey": publicKey,
            "enableDefaultSources": enableDefaultSources,
            "stopLocalRegistry": stopLocalRegistry,
            "createPinnedImageSets": createPinnedImageSets,
            "enableInteractiveFlow": enableInteractiveFlow,
            "useDefaultSourceNames": useDefaultSourceNames,
            "includedOperators": includedOperators,
        }
        filename = f"appliance-config.yaml"
        content = applianceConfigTemplate.render(compiledInputData)
        #print(content)
        with st.expander("appliance-config.yaml"):
            st.code(content, language="yaml")
        with st.expander("appliance-config.yaml - No comments"):
            noCommentContent = ""
            for line in content.splitlines():
                if not line.strip().startswith(("#", "  #")) and line.strip() != "":
                    noCommentContent += line + "\n"
            st.code(noCommentContent, language="yaml")
            st.session_state["configText"] = noCommentContent

st.divider()

st.header("Image Builder")

generatedConfig = st.text_area(label="Configuration", disabled=True, value=st.session_state["configText"])
buildName = st.text_input(label="Build Name", placeholder="Defaults to version-arch-time")
generateISO_button = st.button(label="Generate Image", type="primary")

if generateISO_button:
    # Set a default build name if not provided
    if buildName == "":
        buildName = f"{ocpVersion}-{ocpArchitecture}-{int(time.time())}"

    # Create the build directory if it doesn't exist
    build_dir = os.environ.get("BUILD_BASE_PATH", "/data/builds")
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # Set the build path and create it if it doesn't exist
    build_path = os.path.join(build_dir, buildName)
    if not os.path.exists(build_path):
        os.makedirs(build_path)

    # Make a subdirectory for the build assets
    build_assets_path = os.path.join(build_path, "assets")
    if not os.path.exists(build_assets_path):
        os.makedirs(build_assets_path)

    # Create a container output area
    container_output = st.empty()
    response = []

    # Provide some basic feedback
    response.append(f"<strong>Build name:</strong> {buildName}<br />")
    response.append(f"<strong>BUILD_BASE_PATH:</strong> {os.environ.get('BUILD_BASE_PATH')}<br /><hr />")
    response.append(f"<strong>Podman Version:</strong><br /><pre>")

    # Run a test execution of podman to ensure it's available
    process_env = os.environ.copy()
    podmanVersion = subprocess.Popen(["podman", "version"], env=process_env, stdout=subprocess.PIPE)

    while podmanVersion.poll() is None:
        line = podmanVersion.stdout.readline().decode()
        response.append(line)

    response.append(f"</pre><hr />")

    # Check the Openshift Installer version
    response.append(f"<strong>OpenShift Installer Version:</strong><br /><pre>")
    ocpApplianceBuild = subprocess.Popen(["openshift-install", "version"], env=process_env, stdout=subprocess.PIPE)
    while ocpApplianceBuild.poll() is None:
        line = ocpApplianceBuild.stdout.readline().decode()
        response.append(line)

    response.append(f"</pre><hr />")

    # Save the configuration to a file
    config_file_path = os.path.join(build_path, "appliance-config.yaml")
    with open(config_file_path, "w") as config_file:
        config_file.write(st.session_state["configText"])
    # Save it to the place where the actual appliance build will use it
    config_assets_file_path = os.path.join(build_assets_path, "appliance-config.yaml")
    with open(config_assets_file_path, "w") as config_file:
        config_file.write(st.session_state["configText"])

    response.append(f"<strong>Configuration saved to:</strong> {config_file_path}<br /><hr />")

    progress_bar = st.progress(0, text="Progress...")

    with st.expander("Initialization Output"):
        with st.container(key="init_output"):
            st.html("".join(response))

    progress_bar.progress(10, text="Pulling Appliance Image...")

    # Pull the appliance image
    pull_output = st.empty()
    pull_response = []
    pull_response.append(f"<strong>Pulling Appliance Image:</strong><br /><pre>")

    appliancePull_cmd = subprocess.Popen(["podman", "pull", os.environ.get('APPLIANCE_IMAGE')], env=process_env, stdout=subprocess.PIPE)
    while appliancePull_cmd.poll() is None:
        line = appliancePull_cmd.stdout.readline().decode()
        pull_response.append(line)

    with st.expander("Podman Image Pull Output"):
        with st.container(key="pull_output"):
            pull_output.html("".join(pull_response))
    progress_bar.progress(20, text="Building Appliance Image...")

    podmanApplianceImageBuild_cmd = [
        "podman",
        "run",
        "--rm",
        "-it",
        "--privileged",
        "--net=host",
        "-v",
        "/etc/pki:/etc/pki:ro",
        "--env-host",
        "-v",
        f"{build_assets_path}:/assets:Z",
        f"{os.environ.get('APPLIANCE_IMAGE')}",
        "build",
        "--log-level",
        "debug",
    ]

    build_output = st.empty()
    build_response = []
    build_response.append(f"<strong>Building Appliance Image:</strong><br /><pre>")
    applianceBuild_cmd = subprocess.Popen(podmanApplianceImageBuild_cmd, env=process_env, stdout=subprocess.PIPE)
    while applianceBuild_cmd.poll() is None:
        line = applianceBuild_cmd.stdout.readline().decode()
        build_response.append(line)

    with st.expander("Image Build Output"):
        with st.container(key="build_output"):
            build_output.html("".join(build_response))