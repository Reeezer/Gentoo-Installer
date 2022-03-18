#!/bin/sh
# WARNING! this file has been generated automatically
set -x

# base system

source /etc/profile || exit 1
# sync portage and update the system
emerge-webrsync || exit 1
eselect profile set default/linux/amd64/17.1 || exit 1
emerge -uDN --with-bdeps=y @world || exit 1
# timezone
echo Europe/Zurich > /etc/timezone || exit 1
emerge --config sys-libs/timezone-data || exit 1
env-update || exit 1
source /etc/profile || exit 1

# kernel

# install kernel
emerge sys-kernel/installkernel-gentoo || exit 1
emerge sys-kernel/gentoo-kernel-bin || exit 1

# system config


# system tools


# bootloader


# finalize

