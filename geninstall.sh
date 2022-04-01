#!/bin/sh

# cleanup previous files
rm -r autogen
rm install.tar.gz

# generate new scripts
mkdir autogen
python src/installer/gentooconfig.py

cp misc/done.txt autogen

dos2unix autogen/install.sh
dos2unix autogen/chroot.sh
dos2unix autogen/disks.sfdisk
dos2unix autogen/fstab.txt

cp -r etc/ autogen/
find autogen/etc -type f -exec dos2unix {} \;

tar czfv install.tar.gz  autogen/*
