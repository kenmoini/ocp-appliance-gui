FROM registry.access.redhat.com/ubi9/python-311:1-66
WORKDIR /opt/app-root/src/gui

##################################################################################
# Setup the container environment
USER root

COPY setup/ /opt/app-root/setup/

RUN dnf update -y \
 && dnf install -y podman fuse-overlayfs --exclude container-selinux \
 && dnf clean all \
 && rm -rf /var/cache /var/log/dnf* /var/log/yum.* \
 && DEST_MODE="system" /opt/app-root/setup/download-ocp-binaries.sh

RUN echo default:10000:5000 > /etc/subuid; \
 echo default:10000:5000 > /etc/subgid;

##################################################################################
# Install application dependencies
USER default
RUN pip install -r /opt/app-root/setup/requirements.txt

##################################################################################
# Copy over application files and set permissions
USER root
COPY src/ /opt/app-root/src/gui/
RUN chown -R default:root /opt/app-root/src/gui

##################################################################################
# Final container composition
USER default
EXPOSE 8501

# Rootful container store
VOLUME /var/lib/containers
# Rootless container store
VOLUME /home/default/.local/share/containers
# Asset directory
VOLUME /data

ENTRYPOINT ["/opt/app-root/src/gui/entrypoint.sh"]