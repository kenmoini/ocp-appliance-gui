#!/bin/bash

IMG="registry.access.redhat.com/ubi9/nginx-124:9.5-1741661744"
WWW_ROOT="/opt/appliance-builds"
HTTP_HOST_PORT=8085

cat > nginx.conf <<EOF
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /run/nginx.pid;
include /usr/share/nginx/modules/*.conf;
events {
    worker_connections 1024;
}
http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;
    sendfile            on;
    tcp_nopush          on;
    keepalive_timeout   65;
    types_hash_max_size 4096;
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    include /opt/app-root/etc/nginx.d/*.conf;
    server {
        listen       8080 default_server;
        listen       [::]:8080 default_server;
        server_name  _;
        root         /opt/app-root/src;
        autoindex on;
        autoindex_exact_size off;
        include /opt/app-root/etc/nginx.default.d/*.conf;
    }
}
EOF

podman run --name dropbox -it -d \
 -p ${HTTP_HOST_PORT}:8080 \
 -v ${WWW_ROOT}:/opt/app-root/src:Z \
 -v ./nginx.conf:/etc/nginx/nginx.conf:Z \
 $IMG nginx -g "daemon off;"
