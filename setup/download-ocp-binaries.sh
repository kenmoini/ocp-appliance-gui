#!/bin/bash

# This script downloads the latest OCP binaries for the current platform
# and extracts them into the system or local ./bin directory.

DEST_MODE=${DEST_MODE:="local"} # local or system
CHANNEL=${CHANNEL:="latest"} # latest, stable, stable-4.20, etc
BUTANE_CHANNEL=${BUTANE_CHANNEL:="latest"} # latest, v0.23.0-0, etc

# Set the target platform if not set
if [ -z "$TARGETPLATFORM" ]; then
  ARCH=$(arch)
  OS=$(uname -o | sed 's|GNU/L|l|')
  TARGETPLATFORM="${OS,}/${ARCH,}"
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

# Print some debug info
echo "$TARGETPLATFORM - Building for ARCH: $ARCH | IARCH: $IARCH | OS: $OS"
echo "Operating in $DEST_MODE mode, extracting to $DEST_DIR"

# Create a temporary directory to download and extract the binaries
mkdir -p $DEST_DIR/ocpbintmp
cd $DEST_DIR/ocpbintmp

# Get Base and common multi-arch files
# Butane defaults to latest since it doesn't follow OCP versions
wget https://mirror.openshift.com/pub/openshift-v4/clients/butane/${BUTANE_CHANNEL}/${BUTANE_FILENAME}
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/${OPENSHIFT_INSTALL_FILENAME}.tar.gz
wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/${OPENSHIFT_CLIENT_FILENAME}.tar.gz
wget https://github.com/mikefarah/yq/releases/latest/download/${YQ_BIN_NAME} -O yq

# Get additional files for x86_64 - rather things that don't have an Arm64 build
if [ "$ARCH" = "x86_64" ] && [ "$OS" = "linux" ]; then
  wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/oc-mirror.rhel9.tar.gz
  wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/opm-linux-rhel9.tar.gz
  wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${CHANNEL}/ccoctl-linux.tar.gz
  wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/latest/oc-mirror.rhel9.tar.gz
fi
# Get additional files for arm64
if [ "$ARCH" = "arm64" ] && [ "$OS" = "linux" ]; then
  wget https://mirror.openshift.com/pub/openshift-v4/aarch64/clients/ocp/latest/oc-mirror.rhel9.tar.gz
fi

# Extract the files
for t in *.tar.gz; do
  tar zxvf $t
  rm -vf $t
  rm -vf README.md
done

# Normalize names and set some permissions
mv ${BUTANE_FILENAME} butane
chmod a+x oc kubectl openshift-install butane oc-mirror yq
mv oc kubectl openshift-install butane oc-mirror yq ..

# Additional files for x86_64
if [ "$ARCH" = "x86_64" ]; then
  mv opm-rhel9 opm
  chmod a+x opm ccoctl
  mv opm ccoctl ..
fi

# Clean up
cd ..
rm -rf ocpbintmp