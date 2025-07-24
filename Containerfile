FROM registry.access.redhat.com/ubi9/python-311:1-66
WORKDIR /opt/app-root/src/gui

##################################################################################
# Setup the container environment
USER root

# Rootful container store
VOLUME /var/lib/containers
# Rootless container store
VOLUME /opt/app-root/src/.local/share/containers
# Podman run root?!??
VOLUME /tmp/storage-run-1001/containers
# Asset directory
VOLUME /data

COPY setup/ /opt/app-root/setup/

RUN dnf update -y \
 && dnf reinstall -y shadow-utils \
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
ADD https://raw.githubusercontent.com/containers/image_build/refs/heads/main/podman/containers.conf /etc/containers/containers.conf
ADD https://raw.githubusercontent.com/containers/image_build/refs/heads/main/podman/podman-containers.conf /opt/app-root/src/.config/containers/containers.conf
COPY src/ /opt/app-root/src/gui/
RUN mkdir -p /opt/app-root/src/{.config,.local} \
 && chown default:root -R /opt/app-root/src/ /opt/app-root/src/.config /opt/app-root/src/.local /tmp/storage-run-1001 \
 && chmod 755 /tmp/storage-run-1001

# chmod containers.conf and adjust storage.conf to enable Fuse storage.
RUN chmod 644 /etc/containers/containers.conf; sed -i -e 's|^#mount_program|mount_program|g' -e '/additionalimage.*/a "/var/lib/shared",' -e 's|^mountopt[[:space:]]*=.*$|mountopt = "nodev,fsync=0"|g' /etc/containers/storage.conf
RUN mkdir -p /var/lib/shared/overlay-images /var/lib/shared/overlay-layers /var/lib/shared/vfs-images /var/lib/shared/vfs-layers; touch /var/lib/shared/overlay-images/images.lock; touch /var/lib/shared/overlay-layers/layers.lock; touch /var/lib/shared/vfs-images/images.lock; touch /var/lib/shared/vfs-layers/layers.lock

ENV _CONTAINERS_USERNS_CONFIGURED=""

##################################################################################
# Final container composition
USER default
EXPOSE 8501

ENTRYPOINT ["/opt/app-root/src/gui/entrypoint.sh"]