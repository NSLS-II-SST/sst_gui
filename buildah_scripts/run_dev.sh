#! /usr/bin/bash
set -e
set -o xtrace

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
host_package_dir=$(dirname "$script_dir")/src
container_package_dir=/usr/local/src/sst_gui


XAUTH=/tmp/.docker.xauth
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

podman run --pod acquisition \
       -dt -v /tmp/.X11-unix/:/tmp/.X11-unix/ \
       -e DISPLAY \
       -v $XAUTH:$XAUTH \
       -e XAUTHORITY=$XAUTH \
       -e XDG_RUNTIME_DIR=/tmp/runtime-$USER \
       -e EPICS_CA_ADDR_LIST=10.0.2.255 \
       -e EPICS_CA_AUTO_ADDR_LIST=no \
       --name qs-gui-dev \
       -v $host_package_dir:$container_package_dir \
       sst_gui_dev:latest bash
