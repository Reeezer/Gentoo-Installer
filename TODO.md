# TODO

- Split the config readers into two separate classes (one for system, the other for the drives)
- Copy gentoo's repo config in portage's directories
- Ask confirmation before overwriting partitions
- Check usage of `dist-kernel` use flag
- Add some sort of config validator that ensures the options are used in proper combinations (and also that package names like distkernel actually exist)
- Make a folder of default config files (like make.default.conf)
- Add an option "default" for the file parameter of config files (if anything else than 'default' is used it's interpreted as a file name, otherwise it takes it from a default file)
- Add multi-drive support
