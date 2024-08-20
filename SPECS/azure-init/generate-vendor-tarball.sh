#!/bin/bash -e

# This script is used to generate the vendor tarball for libazureinit

# For generating tar of releases
SOURCE_VERSION="0.1.1"
SOURCE_VERSION_V="v${SOURCE_VERSION}"
SOURCE_URL="https://github.com/Azure/azure-init/archive/refs/tags/${SOURCE_VERSION_V}.tar.gz"

# For generating tar of PRs and Forks
# FORK_OWNER="Azure"
# SOURCE_VERSION="7142bced859169553e8948497aa13df742aac1ff"
# SOURCE_URL="https://github.com/${FORK_OWNER}/azure-init/archive/${SOURCE_VERSION}.tar.gz"

workdir=$(mktemp -d)
cp 0001-add-Azure-Linux-support.patch $workdir/

pushd $workdir
wget $SOURCE_URL
tar -xzvf "${SOURCE_VERSION_V}.tar.gz"
pushd "azure-init-${SOURCE_VERSION}"
patch -p1 < ../0001-add-Azure-Linux-support.patch
cargo vendor >> cargo-config
tar -czvf azure-init-${SOURCE_VERSION}-vendor.tar.gz vendor
popd
popd
mv $workdir/azure-init-${SOURCE_VERSION}/azure-init-${SOURCE_VERSION}-vendor.tar.gz ./azure-init-${SOURCE_VERSION}-vendor.tar.gz
mv $workdir/azure-init-${SOURCE_VERSION}/cargo-config .
mv $workdir/${SOURCE_VERSION_V}.tar.gz ./azure-init-${SOURCE_VERSION}.tar.gz
rm -rf $workdir
