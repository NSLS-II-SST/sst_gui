#! /usr/bin/bash
set -e
set -o xtrace


script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
host_package_dir=$(dirname "$script_dir")/src
container_package_dir=/usr/local/src/sst_gui

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

buildah copy $container $host_package_dir $container_package_dir 
buildah run --workingdir $container_package_dir $container -- pip3 install .

#buildah config --cmd "sst-gui --config /usr/local/src/sst_gui/sst_gui/test_config.yaml" $container

buildah unmount $container

buildah commit $container sst_gui:$version
buildah commit $container sst_gui:latest

buildah rm $container
