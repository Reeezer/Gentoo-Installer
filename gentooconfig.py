from configparser import ConfigParser

from shellwriter import ShellWriter
from sfdisk import SFDisk
from mount import Mount

class GentooConfig:
    """Configuration class for Gentoo
    
    All install actions begin with act_ and are mapped to the handbook sections
    """
    
    # FIXME currently it is only possible to install to a single drive
    
    def __init__(self, configpath):
        self.shellwriter = ShellWriter('install.sh')
        self.configparser = ConfigParser()
        self.configpath = configpath
                
    def finalize(self):
        self.shellwriter.finalize()
        
    def genconfig(self):
        self.load_config()
        
        self.setup_partitions()
        self.setup_file_variables()
        
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
        # read the config from the file
        self.configparser.read(self.configpath)
        
        self.arch = self.configparser.get('gentoo', 'arch', fallback='amd64')
        self.initsystem = self.configparser.get('gentoo', 'initsystem', fallback='openrc')
        # TODO add EFI/BIOS option
        
        self.drive = self.configparser.get('drive', 'drive', fallback='/dev/sda')
        self.drivesize = self.configparser.getint('drive', 'size', fallback=8192)
        self.drivelabel = self.configparser.get('drive', 'label', fallback='gpt')
        
        # TODO allow using this in make.conf
        self.mirror = self.configparser.get('mirror', 'url', fallback="https://mirror.init7.net") # FIXME find a better default mirror, see if it's possible to use gentoo's bouncer
        
        self.profile = self.configparser.get('portage', 'profile', fallback="default/linux/amd64/17.1")
        
        self.timezone = self.configparser.get('timezone', 'timezone', fallback="Europe/Zurich") # FIXME find a better fallback
        
        # generate additional config
        
        self.mirror_base_url = f"{self.mirror}/gentoo/releases/{self.arch}/autobuilds"
        self.latest_stage3_url = f"{self.mirror_base_url}/latest-stage3-{self.arch}-{self.initsystem}.txt"
        
        # FIXME use actual config
        self.partitions = [
            { "name" : "grub", "mountpoint" : "",               "size" :    2, "bootable" : False,  "filesystem" : ""}, # FIXME honestly not sure how to use that partition, should it be bootable?
            { "name" : "boot", "mountpoint" : "/boot",          "size" :  200, "bootable" : True , "filesystem" : "ext2"},
            { "name" : "root", "mountpoint" : "/",              "size" :   -1, "bootable" : False, "filesystem" : "ext4"},
        ]
        
        
    # pre-install setup (like variables and needed generated files)

    def setup_partitions(self):
        """uses SFDisk to generate a script file for sfdisk, also adds the drive path in dev to each partition"""
        
        sfdisk = SFDisk(self.drivelabel, self.drive, self.drivesize)
        for partition in self.partitions:
            # addpart returns the drive string
            partition['drive'] = sfdisk.addpart(**partition)
                
        with open("disks.sfdisk", "w") as sfconfig:
            sfconfig.write(sfdisk.dumpsconfig())

    def setup_file_variables(self):
        self.shellwriter.add_comment("file contents in variables", space=True)
        
        self.shellwriter.add_filevar('MAKECONF_CONTENT', 'make.conf')
        self.shellwriter.add_filevar('SFDISK_FILE_CONTENT', 'disks.sfdisk')
    
    # main install actions

    # no network for now    
    # def act_network():
    #     pass
    
    def act_disks(self):
        self.shellwriter.add_comment("disks and partitions", space=True)
                
        self.partition_drive()
        self.format_drive()
        self.mount_partitions('/mnt/gentoo')
    
    def act_stage3(self):
        self.shellwriter.add_comment("stage3", space=True)
        
        self.cd_root()
        self.download_stage3()
        self.untar_stage3()
    
    def act_basesystem(self):
        self.shellwriter.add_comment("base system", space=True)
        
        self.portage()
        self.chroot()
        self.emerge_sync()
        self.set_timezone()
        self.set_locales()
    
    def act_kernel(self):
        self.shellwriter.add_comment("kernel", space=True)
        # TODO
        # either use genkernel or allow placing the kernel config as an extra file (or maybe just include the whole kernel config in the install script if you don't mind monster files)
    
    def act_sysconfig(self):
        self.shellwriter.add_comment("system config", space=True)
        # TODO
    
    def act_systools(self):
        self.shellwriter.add_comment("system tools", space=True)
        # TODO
    
    def act_bootloader(self):
        self.shellwriter.add_comment("bootloader", space=True)
        # TODO
    
    def act_finalize(self):
        self.shellwriter.add_comment("finalize", space=True)
        # TODO

    ## disks

    def partition_drive(self):
        self.shellwriter.add_comment("partition the drive")            
        self.shellwriter.add_command(f"echo -e $SFDISK_FILE_CONTENT | sfdisk {self.drive}")
    
    def format_drive(self):
        self.shellwriter.add_comment("format the partitions")
        
        for i, partition in enumerate(self.partitions):
            if partition['filesystem'] == "swap":
                self.shellwriter.add_command(f"mkswap {partition['drive']}")
                self.shellwriter.add_command(f"swapon {partition['drive']}")
            elif partition['filesystem'] == "": # e.g. grub's 2MB at the disk start
                continue
            else:
                self.shellwriter.add_command(f"mkfs.{partition['filesystem']} {partition['drive']}")
        
    def mount_partitions(self, prefix):
        self.shellwriter.add_comment("mount the partitions")
        
        mount = Mount(self.partitions)
        for partition in mount.sorted():
            mountpoint = f"{prefix}{partition['mountpoint']}"
            self.shellwriter.add_command(f"mkdir -p {mountpoint}")
            self.shellwriter.add_command(f"mount {partition['drive']} {mountpoint}")

    # base system
    
    def cd_root(self): # FIXME check if there's a way to avoid having to do this
        self.shellwriter.add_comment("move into the new root")
        
        self.shellwriter.add_command("cd /mnt/gentoo")
    
    def download_stage3(self):
        self.shellwriter.add_comment("download stage3")
        
        # get the file containing the relative path to the latest stage3, only keep the last line and remove anything after the first space since the path is before that space
        self.shellwriter.add_command(f"STAGE3_PATH=$(curl -s {self.latest_stage3_url} | tail -n 1 | cut -d ' ' -f 1)")
        # build the final download url
        self.shellwriter.add_command(f"STAGE3_URL={self.mirror_base_url}/$STAGE3_PATH")
        # finally, download the stage3 using wget
        self.shellwriter.add_command(f"wget $STAGE3_URL")

        # TODO also check stage3 digest
    
    def untar_stage3(self):
        self.shellwriter.add_comment("untar stage3")
        
        self.shellwriter.add_command(f"tar xpvf stage3-*.tar.xz --xattrs-include='*.*' --numeric-owner")

    # base system
    
    def portage(self):
        self.shellwriter.add_comment("portage config")

        self.shellwriter.add_command("echo -e $MAKECONF_CONTENT > /mnt/gentoo/etc/portage/make.conf")
        self.shellwriter.add_command("mkdir -p /mnt/gentoo/etc/portage/repos.conf")
        self.shellwriter.add_command("cp /mnt/gentoo/usr/share/portage/config/repos.conf /mnt/gentoo/etc/portage/repos.conf/gentoo.conf")
    
    def chroot(self):
        self.shellwriter.add_comment("chroot")
        
        self.shellwriter.add_command("cp --dereference /etc/resolv.conf /mnt/gentoo/etc")
        self.shellwriter.add_command("mount --types proc /proc /mnt/gentoo/proc")
        self.shellwriter.add_command("mount --rbind /sys /mnt/gentoo/sys")
        self.shellwriter.add_command("mount --rbind /dev /mnt/gentoo/dev")
        self.shellwriter.add_command("mount --bind /run /mnt/gentoo/run")
        
        if self.initsystem == 'systemd':
            self.shellwriter.add_command("mount --make-rslave /mnt/gentoo/sys")
            self.shellwriter.add_command("mount --make-rslave /mnt/gentoo/dev")
            self.shellwriter.add_command("mount --make-slave /mnt/gentoo/run")

        self.shellwriter.add_command("chroot /mnt/gentoo /bin/bash") # FIXME once chroot is executed the script stops
        self.shellwriter.add_command("source /etc/profile")

    def emerge_sync(self):
        self.shellwriter.add_comment("sync portage and update the system")
        
        self.shellwriter.add_command("emerge-webrsync")
        self.shellwriter.add_command(f"eselect profile set {self.profile}")
        self.shellwriter.add_command("emerge -uDN --with-bdeps=y @world")

    def set_timezone(self):
        self.shellwriter.add_comment("timezone")
        
        if self.initsystem == 'openrc':
            self.shellwriter.add_command(f"echo {self.timezone} > /etc/timezone")
            self.shellwriter.add_command("emerge --config sys-libs/timezone-data")
        elif self.initsystem == 'systemd':
            self.shellwriter.add_command(f"ln -sf ../usr/share/zoneinfo/{self.timezone} /etc/localtime")

    def set_locales(self):
        # TODO
        pass

if __name__ == '__main__':
    genconfig = GentooConfig(configpath='installer.conf')
    genconfig.genconfig()
    genconfig.finalize()
