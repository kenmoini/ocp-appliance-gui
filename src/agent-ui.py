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


if "configText" not in st.session_state:
    st.session_state["configText"] = "To be generated..."

st.title("OpenShift Agent Installer")
st.header("Configuration Generator")

with st.sidebar:
    st.markdown("## Helpful Links")
    st.markdown("[Downloads](https://console.redhat.com/openshift/downloads/)")
    
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
    process_env = os.environ.copy()
    x = subprocess.Popen(["podman", "version"], env=process_env, stdout=subprocess.PIPE)


    container_output = st.empty()
    response = []
    num_lines=0
    while x.poll() is None:
        line = x.stdout.readline().decode()
        num_lines += 1
        response.append(line)

    container_output.write("".join(response))