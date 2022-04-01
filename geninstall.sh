#!/bin/sh

# cleanup previous files
rm -r autogen
rm install.tar.gz

# generate new scripts
mkdir autogen
python src/installer/gentooconfig.py

cp etc/portage/make.conf autogen/
cp misc/done.txt autogen

dos2unix autogen/install.sh
dos2unix autogen/chroot.sh
dos2unix autogen/make.conf
dos2unix autogen/disks.sfdisk
dos2unix autogen/fstab.txt

tar czfv install.tar.gz  autogen/*
