import streamlit as st
from jinja2 import Environment, FileSystemLoader
import os, time, subprocess

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
if "configText" not in st.session_state:
    st.session_state["configText"] = "To be generated..."

if 'current_step' not in st.session_state:
    st.session_state['current_step'] = 1

if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'Grid'

# Load CSS
with open('./static/custom.css') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Page configuration
st.title("OpenShift Agent Installer")
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