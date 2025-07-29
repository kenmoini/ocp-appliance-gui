import streamlit as st
from jinja2 import Environment, FileSystemLoader
import os, time, subprocess
from io import StringIO

# Setup Jinja2 environment for templating
environment = Environment(loader=FileSystemLoader("templates/"))
installConfigTemplate = environment.get_template("install-config.yaml.j2")
agentConfigTemplate = environment.get_template("agent-config.yaml.j2")

# Defaults
enableDefaultSources = False
stopLocalRegistry = False
createPinnedImageSets = False
enableInteractiveFlow = False
useDefaultSourceNames = False


# Set default values for session state
if "sshPubKey" not in st.session_state:
    st.session_state["sshPubKey"] = " "
if "additionalTrustBundle" not in st.session_state:
    st.session_state["additionalTrustBundle"] = "\n"
if "configText" not in st.session_state:
    st.session_state["configText"] = "To be generated..."

if 'current_step' not in st.session_state:
    st.session_state['current_step'] = 1

if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'Grid'

### maintains the user's location within the wizard
def set_form_step(action,step=None):
    if action == 'Next':
        st.session_state['current_step'] = st.session_state['current_step'] + 1
    if action == 'Back':
        st.session_state['current_step'] = st.session_state['current_step'] - 1
    if action == 'Jump':
        st.session_state['current_step'] = step

### used to toggle back and forth between Grid View and Form View
def set_page_view(target_view):
    st.session_state['current_view'] = target_view

# Load CSS
with open('./static/custom.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Load the enabled versions of the openshift-installer binaries
if os.path.exists("../bin/versioned-bin"):
    # Loop through the folders and return the names of them
    versionedBinPath = "../bin/versioned-bin"
    ocpVersions = [d for d in os.listdir(versionedBinPath) if os.path.isdir(os.path.join(versionedBinPath, d))]
    ocpVersions.sort(reverse=True)  # Sort versions in descending order

# Page configuration
st.title("OpenShift Agent Installer")
st.header("Configuration Generator")

with st.sidebar:
    st.markdown("## Helpful Links")
    st.markdown("[Downloads](https://console.redhat.com/openshift/downloads/)")
    st.markdown("[Update Graph](https://access.redhat.com/labs/ocpupgradegraph/update_path/)")
    st.markdown("[OpenShift Pull Secret](https://console.redhat.com/openshift/install/pull-secret)")
    
col1, col2 =st.columns(2)
with col1:
    ocpVersion = st.selectbox(label="OpenShift Version", 
                                options=ocpVersions,index=0)
    ocpArchitecture = st.selectbox(label="CPU Architecture", 
                                options=["x86_64","aarch64","ppc64le"],index=0)

with col2:
    coreUserPass = st.text_input(label="core User Password")
    fipsMode = st.selectbox(label="FIPS Mode", 
                                    options=["Disabled", "Enabled"],index=0)

pullSecret = st.text_input(label="OpenShift Pull Secret", type="password")


with st.expander("SSH Public Key Configuration"):
        
    def processPubKeyUpload(uploaded_file):
        content = uploaded_file.read().decode("utf-8")
        st.session_state["sshPubKey"] = content

    def syncPubKeyUpload():

        content = uploadedPublicKeyFile.read().decode("utf-8")
        st.session_state["sshPubKey"] = content

    publicKey = st.text_input(label="SSH Public Key", value=f"{st.session_state["sshPubKey"]}")

    uploadedPublicKeyFile = st.file_uploader("Or choose a Public Key file")

    if uploadedPublicKeyFile:
        processPubKeyUpload(uploadedPublicKeyFile)


with st.expander("General Network Configuration"):
    dnsServers = st.multiselect(
        "DNS Servers",
        [],
        max_selections=3,
        accept_new_options=True,
    )
    dnsSearchDomains = st.multiselect(
        "DNS Search Domains",
        [],
        max_selections=3,
        accept_new_options=True,
    )
    ntpServers = st.multiselect(
        "NTP Servers",
        [],
        max_selections=3,
        accept_new_options=True,
    )
    clusterNetwork = st.text_input(
        label="Cluster Network",
        value="10.128.0.0/14",
        help="Overall CIDR space for the Pods in the cluster",
    )
    clusterHostNetworkPrefix = st.selectbox(
        label="Cluster Host Network Prefix",
        options=["/20", "/21", "/22", "/23", "/24", "/25", "/26", "/27", "/28"],
        index=3,
        help="CIDR prefix for each host's pool of Pod IPs from the overall Cluster Network CIDR",
    )
    serviceNetworkCIDRs = st.multiselect(
        "Service Network CIDRs",
        ["172.30.0.0/16"],
        default=["172.30.0.0/16"],
        help="CIDRs for the Services in the cluster",
        max_selections=5,
        accept_new_options=True,
    )
    machineNetworkCIDRs = st.multiselect(
        "Machine Network CIDRs",
        [],
        help="CIDRs for the machines in the cluster, the network the hosts live in",
        max_selections=5,
        accept_new_options=True,
    )

with st.expander("Certificate Authority Configuration"):
    caCertBundle = st.text_area(
        label="CA Certificate Bundle",
        value=st.session_state["additionalTrustBundle"],
        help="PEM-encoded CA certificate bundle for the cluster",
        height=200,
    )
    #uploadedCertificateBundles = st.file_uploader("Or upload files", accept_multiple_files=True)
    #for uploaded_file in uploadedCertificateBundles:
    #    bytes_data = uploaded_file.read()
    #    #st.write(bytes_data)
    #    certData = "# " + uploaded_file.name + "\n" + bytes_data.decode("utf-8") + "\n"
    #    st.session_state["additionalTrustBundle"] += certData


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
            "fipsMode": fipsMode,
            "pullSecret": pullSecret,
            "publicKey": publicKey,
        }
        installConfigContent = installConfigTemplate.render(compiledInputData)
        agentConfigContent = agentConfigTemplate.render(compiledInputData)

        with st.expander("install-config.yaml"):
            st.code(installConfigContent, language="yaml")
        with st.expander("agent-config.yaml"):
            st.code(agentConfigContent, language="yaml")