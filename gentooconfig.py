from configparser import ConfigParser

from shellwriter import ShellWriter
from sfdisk import SFDisk
from mount import Mount

class GentooConfig:
    """Configuration class for Gentoo
    
    All install actions begin with act_ and are mapped to the handbook sections
    """
    
    # FIXME currently it is only possible to install to a single drive
    
    def __init__(self, sysconfigpath, driveconfigpath):
        self.baseshell = ShellWriter('install.sh')  # prepares the disks and 
        self.chrootshell = ShellWriter('chroot.sh') # system install inside the chroot
        
        self.sysconfigparser = ConfigParser()
        self.sysconfigpath = sysconfigpath
        
        self.driveconfigparser = ConfigParser()
        self.driveconfigpath = driveconfigpath
                
    def finalize(self):
        self.baseshell.finalize()
        self.chrootshell.finalize()
        
    def genconfig(self):
        self.load_config()
        
        self.setup_partitions()
        
        self.act_network()
        self.act_disks()
        self.act_stage3()
        self.act_basesystem()
        self.act_kernel()
        self.act_sysconfig()
        self.act_systools()
        self.act_bootloader()
        self.act_finalize()
        
    # config
    
    def load_config(self):
        self.load_gentoo_config()
        self.load_disks_config()
        
    def load_disks_config(self):
        self.driveconfigparser.read(self.driveconfigpath)
        
        self.partitions = []
        
        for section in self.driveconfigparser.sections():
            if section == 'general':
                self.drive = self.driveconfigparser.get('general', 'drive', fallback='/dev/sda')
                self.drivesize = self.driveconfigparser.getint('general', 'size', fallback=8192)
                self.drivelabel = self.driveconfigparser.get('general', 'label', fallback='gpt')
            else:
                name = section
                mountpoint = self.driveconfigparser.get(section, 'mountpoint', fallback='') # fallback = no mountpoint, e.g. swap
                size = int(self.driveconfigparser.get(section, 'size', fallback=-1))
                filesystem = self.driveconfigparser.get(section, 'filesystem', fallback='')
                bootable = int(self.driveconfigparser.get(section, 'bootable', fallback=0))
                
                self.partitions.append({
                    'name': name,
                    'mountpoint' : mountpoint,
                    'size' : size,
                    'filesystem' : filesystem,
                    'bootable': bootable
                })
        
    def load_gentoo_config(self):
        self.sysconfigparser.read(self.sysconfigpath)
            
        self.architecture = self.sysconfigparser.get('gentoo', 'arch', fallback='amd64')
        self.initsystem = self.sysconfigparser.get('gentoo', 'initsystem', fallback='openrc')
        # TODO add EFI/BIOS option
        
        # TODO allow using this in make.conf
        self.mirror = self.sysconfigparser.get('mirror', 'url', fallback="https://mirror.init7.net") # FIXME find a better default mirror, see if it's possible to use gentoo's bouncer
        
        self.profile = self.sysconfigparser.get('portage', 'profile', fallback="default/linux/amd64/17.1")
        
        self.timezone = self.sysconfigparser.get('timezone', 'timezone', fallback="Europe/Zurich") # FIXME find a better fallback
        
        self.kernel_configmode = self.sysconfigparser.get('kernel', 'config', fallback='distkernel')
        self.distkernel_package = self.sysconfigparser.get('kernel', 'distkernel', fallback='kernel-gentoo-bin')

        # generate additional config
        self.mirror_base_url = f"{self.mirror}/gentoo/releases/{self.architecture}/autobuilds"
        self.latest_stage3_url = f"{self.mirror_base_url}/latest-stage3-{self.architecture}-{self.initsystem}.txt"
        
    # pre-install setup (like variables and needed generated files)

    def setup_partitions(self):
        """uses SFDisk to generate a script file for sfdisk, also adds the drive path in dev to each partition"""
        
        sfdisk = SFDisk(self.drivelabel, self.drive, self.drivesize)
        for partition in self.partitions:
            # addpart returns the drive string
            partition['drive'] = sfdisk.addpart(**partition)
                
        with open("disks.sfdisk", "w") as sfconfig:
            sfconfig.write(sfdisk.dumpsconfig())

    # main install actions

    def act_network(self):
        self.baseshell.add_comment("network", space=True)
        self.ntp_sync()
    
    def act_disks(self):
        self.baseshell.add_comment("disks and partitions", space=True)
                
        self.partition_drive()
        self.format_drive()
        self.mount_partitions('/mnt/gentoo')
    
    def act_stage3(self):
        self.baseshell.add_comment("stage3", space=True)

        self.download_stage3()
        self.untar_stage3()
    
    def act_basesystem(self):
        self.baseshell.add_comment("base system", space=True)
        self.chrootshell.add_comment("base system", space=True)
        
        self.portage()
        self.chroot()
        self.emerge_sync()
        self.set_timezone()
        self.set_locales()
    
    def act_kernel(self):
        self.chrootshell.add_comment("kernel", space=True)
        self.install_kernel()
    
    def act_sysconfig(self):
        self.chrootshell.add_comment("system config", space=True)
        self.generate_fstab()
    
    def act_systools(self):
        self.chrootshell.add_comment("system tools", space=True)
        # TODO
    
    def act_bootloader(self):
        self.chrootshell.add_comment("bootloader", space=True)
        # TODO
    
    def act_finalize(self):
        self.chrootshell.add_comment("finalize", space=True)
        # TODO
        
    ## network
    
    def ntp_sync(self):
        self.baseshell.add_comment("synchronize time using NTP")
        self.baseshell.add_command("ntpd -g -q")
        
    ## disks

    def partition_drive(self):
        self.baseshell.add_comment("partition the drive")            
        self.baseshell.add_command(f"cat disks.sfdisk | sfdisk {self.drive}")
    
    def format_drive(self):
        self.baseshell.add_comment("format the partitions")
        
        for i, partition in enumerate(self.partitions):
            if partition['filesystem'] == "swap":
                self.baseshell.add_command(f"mkswap {partition['drive']}")
                self.baseshell.add_command(f"swapon {partition['drive']}")
            elif partition['filesystem'] == "": # e.g. grub's 2MB at the disk start
                continue
            else:
                self.baseshell.add_command(f"mkfs.{partition['filesystem']} {partition['drive']}")
        
    def mount_partitions(self, prefix):
        self.baseshell.add_comment("mount the partitions")
        
        mount = Mount(self.partitions)
        for partition in mount.sorted():
            mountpoint = f"{prefix}{partition['mountpoint']}"
            self.baseshell.add_command(f"mkdir -p {mountpoint}")
            self.baseshell.add_command(f"mount {partition['drive']} {mountpoint}")

    # base system
    
    def download_stage3(self):
        self.baseshell.add_comment("download stage3")
        
        # get the file containing the relative path to the latest stage3, only keep the last line and remove anything after the first space since the path is before that space
        self.baseshell.add_command(f"STAGE3_PATH=$(curl -s {self.latest_stage3_url} | tail -n 1 | cut -d ' ' -f 1)")
        # build the final download url
        self.baseshell.add_command(f"STAGE3_URL={self.mirror_base_url}/$STAGE3_PATH")
        # finally, download the stage3 using wget
        self.baseshell.add_command(f"wget $STAGE3_URL")

        # TODO also check stage3 digest
    
    def untar_stage3(self):
        self.baseshell.add_comment("untar stage3")
        
        self.baseshell.add_command(f"tar xpvf stage3-*.tar.xz --xattrs-include='*.*' --numeric-owner --directory /mnt/gentoo")

    # base system
    
    def portage(self):
        self.baseshell.add_comment("portage config")

        self.baseshell.add_command("cp make.conf /mnt/gentoo/etc/portage/make.conf") # FIXME use make.conf from config
        self.baseshell.add_command("mkdir -p /mnt/gentoo/etc/portage/repos.conf")
        self.baseshell.add_command("cp /mnt/gentoo/usr/share/portage/config/repos.conf /mnt/gentoo/etc/portage/repos.conf/gentoo.conf")
    
    def chroot(self):
        self.baseshell.add_comment("chroot")
        
        self.baseshell.add_command("cp --dereference /etc/resolv.conf /mnt/gentoo/etc")
        self.baseshell.add_command("mount --types proc /proc /mnt/gentoo/proc")
        self.baseshell.add_command("mount --rbind /sys /mnt/gentoo/sys")
        self.baseshell.add_command("mount --rbind /dev /mnt/gentoo/dev")
        self.baseshell.add_command("mount --bind /run /mnt/gentoo/run")
        
        if self.initsystem == 'systemd':
            self.baseshell.add_command("mount --make-rslave /mnt/gentoo/sys")
            self.baseshell.add_command("mount --make-rslave /mnt/gentoo/dev")
            self.baseshell.add_command("mount --make-slave /mnt/gentoo/run")

        self.baseshell.add_comment("the install continues in chroot.sh")
        self.baseshell.add_command("chmod +x chroot.sh")
        self.baseshell.add_command("cp chroot.sh /mnt/gentoo/chroot.sh")
        self.baseshell.add_command("chroot /mnt/gentoo ./chroot.sh") # WARNING : the script specified must be a path inside the chroot
        
        # here we switch to the chroot script
        self.chrootshell.add_command("source /etc/profile")

    def emerge_sync(self):
        self.chrootshell.add_comment("sync portage and update the system")
        
        self.chrootshell.add_command("emerge-webrsync")
        self.chrootshell.add_command(f"eselect profile set {self.profile}")
        self.chrootshell.add_command("emerge -uDN --with-bdeps=y @world")

    def set_timezone(self):
        self.chrootshell.add_comment("timezone")
        
        if self.initsystem == 'openrc':
            self.chrootshell.add_command(f"echo {self.timezone} > /etc/timezone")
            self.chrootshell.add_command("emerge --config sys-libs/timezone-data")
        elif self.initsystem == 'systemd':
            self.chrootshell.add_command(f"ln -sf ../usr/share/zoneinfo/{self.timezone} /etc/localtime")
        self.chrootshell.add_command("env-update")
        self.chrootshell.add_command("source /etc/profile")

    def set_locales(self):
        # TODO
        pass
    
    def install_kernel(self):
        self.chrootshell.add_comment("install kernel")
        
        if self.kernel_configmode == 'distkernel': # FIXME add support for bin-distkernel
            # FIXME check what init system is used and install the correct installkernel package
            # FIXME here GRUB + OpenRC is assumed
            self.chrootshell.add_command('emerge sys-kernel/installkernel-gentoo')
            
            self.chrootshell.add_command(f"emerge sys-kernel/{self.distkernel_package}")
        else:
            self.chrootshell.add_command("emerge sys-kernel/linux-firmware") # FIXME only if the user asks to download the firmware
            self.chrootshell.add_command("emerge sys-kernel/gentoo-sources")
            self.chrootshell.add_command("eselect kernel set 1") # there should only be one kernel at this point
            
            if self.kernel_configmode == 'genkernel':
            # FIXME /boot must be in fstab at this point
                self.chrootshell.add_command("emerge sys-kernel/genkernel")
                self.chrootshell.add_command("genkernel all")
                
    def install_modprobe_files(self):
        pass # TODO
    
    def generate_fstab(self):
        pass
    
        
        

if __name__ == '__main__':
    genconfig = GentooConfig(sysconfigpath='installer.conf', driveconfigpath='disks.conf')
    genconfig.genconfig()
    genconfig.finalize()
