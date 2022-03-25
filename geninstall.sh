#!/bin/sh

ODIR=autogen

python src/installer/gentooconfig.py

# cleanup previous files
rm -r $ODIR
rm install.tar.gz

mkdir autogen

cp install.sh $ODIR/
cp chroot.sh $ODIR/
cp etc/portage/make.conf $ODIR/
cp disks.sfdisk $ODIR/
cp fstab.txt $ODIR/

dos2unix $ODIR/install.sh
dos2unix $ODIR/chroot.sh
dos2unix $ODIR/make.conf
dos2unix $ODIR/disks.sfdisk
dos2unix $ODIR/fstab.txt

tar czfv install.tar.gz  $ODIR/*
