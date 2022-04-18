# Conception OS - Commands

---
# Preparing the disks
## Partitioning the disk with GPT for UEFI
### Creating a new disklabel / removing all partitions
```
fdisk /dev/sda

g
```

### Creating the EFI system partition (ESP)
```
n
1
[enter]
+256M

t
1
```

### Creating the swap partition
```
n 
2
[enter]
+4G

t
2
19
```

### Creating the root partition
```
n
3
[enter]
[enter]
```

### Saving the partition layout
```
w
```

## Creating file systems
### Applying a filesystem to a partition
```
mkfs.vfat -F 32 /dev/sda1
mkfs.ext4 /dev/sda3
mkfs.ext4 /dev/sda2
```

## Mounting the root partition
```
mount /dev/sda3 /mnt/gentoo
```

# Installing the Gentoo installation files
## Installing a stage tarball
### Downloading the stage tarball
```
cd /mnt/gentoo
// gérer les mises à jour pour récupérer la dernière
wget https://mirror.init7.net/gentoo/releases/amd64/autobuilds/current-stage3-amd64-openrc/stage3-amd64-openrc-<VERSION NUMBER>.tar.xz
```

### Unpacking the stage tarball
```
tar xpvf stage3-*.tar.xz --xattrs-include='*.*' --numeric-owner
```

## Configuring compile options
```
nano -w /mnt/gentoo/etc/portage/make.conf
// rajouter MAKEOPTS pour parralléliser le tout
// MAKEOPTS="-j2"	
// CTRL S + CTRL X
```

# Installing the Gentoo base system
## Chrooting
### Copy DNS info
```
cp --dereference /etc/resolv.conf /mnt/gentoo/etc/
```

### Mounting the necessary filesystems
```
mount --types proc /proc /mnt/gentoo/proc
mount --rbind /sys /mnt/gentoo/sys
mount --make-rslave /mnt/gentoo/sys
mount --rbind /dev /mnt/gentoo/dev
mount --make-rslave /mnt/gentoo/dev 
mount --bind /run /mnt/gentoo/run
mount --make-slave /mnt/gentoo/run 

test -L /dev/shm && rm /dev/shm && mkdir /dev/shm
mount --types tmpfs --options nosuid,nodev,noexec shm /dev/shm 
chmod 1777 /dev/shm
```

### Entering the new environment
```
chroot /mnt/gentoo /bin/bash
source /etc/profile
export PS1="(chroot) ${PS1}"
```

### Mounting the boot partition
```
mount /dev/sda1 /boot
```

## Configuring Portage
### Installing a Gentoo ebuild repository snapshot from the web
```
emerge-webrsync
```

### Choosing the right profile
```
eselect profile list

eselect profile set <NUMBER | PROFILE_NAME>
```

### Updating the @world set
```
emerge --ask --verbose --update --deep --newuse @world
```

### Configuring the USE variable
```
// rien a faire, juste output pour vérifier
```

### Configuring the ACCEPT_LICENSE variable
```
nano /etc/portage/make.conf
// mettre: ACCEPT_LICENSE="*"
```

## Configure locales
### Locale generation
```
nano -w /etc/locale.gen

en_US ISO-8859-1
en_US.UTF-8 UTF-8
de_DE ISO-8859-1
de_DE.UTF-8 UTF-8

locale-gen
```

### Locale selection
```
nano /etc/env.d/02locale

LANG="de_DE.UTF-8"
LC_COLLATE="C.UTF-8"

env-update && source /etc/profile && export PS1="(chroot) ${PS1}"
```

# Configuring the Linux kernel
## Kernel configuration and compilation
### Installing the sources
```
emerge --ask sys-kernel/gentoo-sources

eselect kernel list
eselect kernel set <NUMBER>
```

### Manual configuration
#### Introduction
```
emerge --ask sys-apps/pciutils

cd /usr/src/linux
make menuconfig
```

#### Activating required options
![](https://i.imgur.com/NFYjGKB.png)
![](https://i.imgur.com/cqrXilV.png)
![](https://i.imgur.com/1C6shot.png)
![](https://i.imgur.com/wjDkmH2.png)
![](https://i.imgur.com/BPixMn3.png)
![](https://i.imgur.com/UagX985.png)
![](https://i.imgur.com/RP25qpq.png)
![](https://i.imgur.com/Zm1adcf.png)
![](https://i.imgur.com/hkM1jRe.png)
![](https://i.imgur.com/OeWe9kU.png)

### Compiling and installing
```
make && make modules_install
make install
```

## Kernel modules
### Configuring the modules
```
find /lib/modules/<kernel version>/ -type f -iname '*.o' -or -iname '*.ko' | less

mkdir -p /etc/modules-load.d 
nano -w /etc/modules-load.d/network.conf 
// put all the names of the modules listed in the file
```

# Configuring the system
## Filesystem information
### Creating the fstab file
```
nano -w /etc/fstab
```
![](https://i.imgur.com/5AB4jgc.png)

## Networking information
### Host and domain information
#### OpenRC
```
nano -w /etc/conf.d/hostname
// change your hostname
// hostname="<NAME>"

// if necessary change domain name
nano -w /etc/conf.d/net
// dns_domain_lo="<NAME>"

// fi necessary set NIS domain name
nano -w /etc/conf.d/net
// nis_domain_lo="<NAME>"
```

#### systemd
```
hostnamectl hostname <NAME>
```
 
Problème: je n'ai pas accès à `hostnamectl`, ni `sudo` pour l'installer

### Network
#### DHCP via dhcpcd (any init system)
```
emerge --ask net-misc/dhcpcd

// problème: wget unable to resolve host address
// solution: nano /etc/resolv.conf
// 			 y mettre 'nameserver 8.8.8.8' en 1e ligne

rc-update add dhcpcd default
rc-service dhcpcd start 

// problème: start-stop-daemon is already running
// solution: 

systemctl enable --now dhcppcd

// problème: systemctl commmand not found (et toujours pas accès à sudo)
// solution:
```

#### netifrc (OpenRC)
```
emerge --ask --noreplace net-misc/netifrc
nano -w /etc/conf.d/net
// put config_eth0="dhcp"

cd /etc/init.d
ln -s net.lo net.eth0
rc-update add net.eth0 default
```

### The hosts file
```
nano -w /etc/hosts
```
![](https://i.imgur.com/m7JTHrg.png)

## System information 
### Root password
```
passwd
// enter a password
```
![](https://i.imgur.com/R2kzNLl.png)

### Init and boot configuration
#### OpenRC
```
nano -w /etc/rc.conf
nano -w /etc/conf.d/keymaps
nano -w /etc/conf.d/hwclock

// in all files change what's needed
```

#### systemd
```
systemd-firstboot --prompt --setup-machine-id
```

# Installing system tools
## System logger
```
emerge --ask app-admin/sysklogd
rc-update add sysklogd default
```

## Filesystem tools
```
emerge --ask sys-fs/e2fsprogs
```

## Networking tools
### Installing a DHCP client
```
emerge --ask net-misc/dhcpcd
```

# Configuring the bootloader
## Selecting a boot loader GRUB2 (default)
### Emerge
```
emerge --ask sys-boot/grub
// ensure GRUB_PLATFORMS="efi-64" is enabled using --verbose (and then remove it before emerging)
```

### Install
```
grub-install /dev/sda
// grub-install --target=x86_64-efi --efi-directory=/boot
```

### Configure
```
grub-mkconfig -o /boot/grub/grub.cfg
```

### Rebooting the system
```
exit

cd
umount -l /mnt/gentoo/dev{/shm,/pts,}
umount -R /mnt/gentoo
reboot
```

# Finalizing
## User administration
### Adding a user for daily use
```
useradd -m -G users,wheel,audio -s /bin/bash <USERNAME>
passwd <USERNAME>
// type 2 times password
```

## Disk cleanup
### Removing tarballs
```
rm /stage3-*.tar.*
```

---
# Genkernel

```

```