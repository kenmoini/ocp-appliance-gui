#!/bin/bash

# Set some default parameters
BIN_VERSION=${BIN_VERSION:=("4.18.20" "4.19.4")}
DEST_MODE=${DEST_MODE:="local"} # local or system
CHANNEL=${CHANNEL:="stable"} # latest, stable, stable-4.20, etc
BUTANE_CHANNEL=${BUTANE_CHANNEL:="latest"} # latest, v0.23.0-0, etc

# Set the target platform if not set
if [ -z "$TARGETPLATFORM" ]; then
  ARCH=$(arch)
  OS=$(uname -o | sed 's|GNU/L|l|')
  TARGETPLATFORM="${OS}/${ARCH}"
fi

# Set the destination directory
if [ "$DEST_MODE" = "system" ]; then
  DEST_DIR="/usr/local/bin"
else
  DEST_DIR="./bin"
fi

# Set the filenames based on the platform - it's not really a standard...
if [ "$TARGETPLATFORM" = "linux/amd64" ] || [ "$TARGETPLATFORM" = "linux/x86_64" ]; then
  ARCH=x86_64
  IARCH=amd64
  OPENSHIFT_INSTALL_FILENAME=openshift-install-linux
  OPENSHIFT_CLIENT_FILENAME=openshift-client-linux
  YQ_BIN_NAME=yq_linux_amd64
  BUTANE_FILENAME=butane-${IARCH}
elif [ "$TARGETPLATFORM" = "linux/arm64" ] || [ "$TARGETPLATFORM" = "linux/aarch64" ]; then
  ARCH=arm64
  IARCH=aarch64
  OPENSHIFT_INSTALL_FILENAME=openshift-install-linux-arm64
  OPENSHIFT_CLIENT_FILENAME=openshift-client-linux-arm64
  YQ_BIN_NAME=yq_linux_arm64
  BUTANE_FILENAME=butane-${IARCH}
elif [ "$TARGETPLATFORM" = "darwin/arm64" ] || [ "$TARGETPLATFORM" = "darwin/aarch64" ]; then
  ARCH=arm64
  IARCH=aarch64
  OPENSHIFT_INSTALL_FILENAME=openshift-install-mac-arm64
  OPENSHIFT_CLIENT_FILENAME=openshift-client-mac-arm64
  YQ_BIN_NAME=yq_darwin_arm64
  # Butane doesn't have a darwin build for arm64?
  BUTANE_FILENAME=butane-darwin-amd64
else
  echo "$TARGETPLATFORM - Building for unsupported platform"
  exit 1
fi

# Navigate into the project root directory
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")
cd "$PROJECT_ROOT" || exit 1

# Navigate to the src directory and make the ocp-bin directory
cd src
mkdir -p bin/tmp
cd bin/tmp

# Get Base and common multi-arch files
# Butane defaults to latest since it doesn't follow OCP versions
wget https://mirror.openshift.com/pub/openshift-v4/clients/butane/${BUTANE_CHANNEL}/${BUTANE_FILENAME}
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/${OPENSHIFT_CLIENT_FILENAME}.tar.gz
wget https://github.com/mikefarah/yq/releases/latest/download/${YQ_BIN_NAME} -O yq

# Get additional files for x86_64 - rather things that don't have an Arm64 build
if [ "$ARCH" = "x86_64" ] && [ "$OS" = "linux" ]; then
  wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/opm-linux-rhel9.tar.gz
  #wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/oc-mirror.rhel9.tar.gz
  #wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/ccoctl-linux.tar.gz
  #wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest/oc-mirror.rhel9.tar.gz
fi
# Get additional files for arm64
#if [ "$ARCH" = "arm64" ] && [ "$OS" = "linux" ]; then
  #wget https://mirror.openshift.com/pub/openshift-v4/aarch64/clients/ocp/latest/oc-mirror.rhel9.tar.gz
#fi

# Extract the files
for t in *.tar.gz; do
  tar zxvf $t
  rm -vf $t
  rm -vf README.md
done

# Move the binaries to the destination directory
mv ${BUTANE_FILENAME} butane
chmod a+x oc kubectl butane yq
mv oc kubectl butane yq ..

# Additional files for x86_64
if [ "$ARCH" = "x86_64" ]; then
  mv opm-rhel9 opm
  chmod a+x opm
  mv opm ..
fi

# Versioned OpenShift Install binaries
cd ..
rm -rf tmp
mkdir -p versioned-bin
cd versioned-bin

# Loop through the BIN_VERSION array and download the corresponding files
for v in "${BIN_VERSION[@]}"; do
  mkdir -p "$v"
  cd "$v"
  wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${v}/${OPENSHIFT_INSTALL_FILENAME}.tar.gz
  wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${v}/${OPENSHIFT_CLIENT_FILENAME}.tar.gz
  tar zxvf ${OPENSHIFT_INSTALL_FILENAME}.tar.gz
  tar zxvf ${OPENSHIFT_CLIENT_FILENAME}.tar.gz
  rm -vf ${OPENSHIFT_INSTALL_FILENAME}.tar.gz ${OPENSHIFT_CLIENT_FILENAME}.tar.gz README.md
  chmod a+x openshift-install kubectl oc
done

