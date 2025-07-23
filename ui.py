import streamlit as st
from jinja2 import Environment, FileSystemLoader
import os
import subprocess
#import boto3
#from botocore.exceptions import ClientError


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

st.title("OpenShift Appliance Installer")
st.header("Configuration Generator")

with st.sidebar:
    st.markdown("## Helpful Links")
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
    if buildName == "":
        buildName = f"{ocpVersion}-{ocpArchitecture}-{int(os.time())}"