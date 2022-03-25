# TODO

## Important

- By default no user account is created and the root password is empty, allow giving a password in an encrypted manner
- Make it possible to specify additional packages to install
- Add wireless internet support
- Make the installer fail if invalid options are used

## Secondary

- Split the config readers into two separate classes (one for system, the other for the drives)
- Copy gentoo's repo config in portage's directories
- Ask confirmation before overwriting partitions
- Check usage of `dist-kernel` use flag
- Add some sort of config validator that ensures the options are used in proper combinations (and also that package names like distkernel actually exist)
- Make a folder of default config files (like make.default.conf)
- Add an option "default" for the file parameter of config files (if anything else than 'default' is used it's interpreted as a file name, otherwise it takes it from a default file)
- Add multi-drive support
- x.org keyboard config
- module rebuilds after kernel update
- for fstab and sfdisk use disk labels (or even UUID if possible) instead of device path
- add fstab options in disks.conf
- allow other network options than dhcpcd
- add PCMCIA support
- add /etc/rc.conf support
- add /etc/conf.d/keymaps support
- add hwclock support

## Nice to have

- Allow using other loggers with systemd
