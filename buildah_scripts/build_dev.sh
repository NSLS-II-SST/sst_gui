#! /usr/bin/bash
set -e
set -o xtrace


script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
host_package_dir=$(dirname "$script_dir")/src
container_script_dir=/usr/local/bin

version="0.0.1"

# Check if bluesky:latest image is available locally
if [[ "$(buildah images -q sst:latest)" == "" ]]; then
  echo "Image not found locally. Pulling from ghcr.io/nsls-ii-sst..."
  buildah pull ghcr.io/nsls-ii-sst/sst:latest
fi

container=$(buildah from sst)
buildah run $container -- dnf -y install qt5-qtbase-devel
buildah run $container -- conda install -y pyqt
buildah run $container -- pip3 install bluesky_queueserver_api qtconsole
buildah copy $container $script_dir/run_dev.sh $container_script_dir
buildah config --cmd "bash $container_script_dir/run_dev.sh" $container


buildah unmount $container

buildah commit $container sst_gui_dev:$version
buildah commit $container sst_gui_dev:latest

buildah rm $container
