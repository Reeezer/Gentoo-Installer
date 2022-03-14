#!/bin/bash

# FIXME use an env variable to decide whether to use genkernel or not?
# 0 - copy our pre-configured config
# cp kconfig.conf /usr/src/linux/.config

# 1 - configure kernel
make silentoldconfig

# 2 - compile kernel
make -j5
make modules_install

# 3 - make sure /boot is mounted, if not attempt to mount it
if [ mountpoint -q /boot || mount /boot ]; then
    echo "[info]  /boot mounted"
else
    echo "[error] cannot mount /boot" >&2
    exit 1
fi

# 4 - copy the kernel image to /boot
make install

# 5 - update bootloader config, assuming grub is used
grub-mkconfig -o /boot/grub/grub.cfg
