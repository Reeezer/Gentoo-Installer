class FSTab:
    """Generates a /etc/fstab valid file from given partitions"""
    
    def __init__(self, partitions:list):
        self.partitions = partitions
        
    def dumps(self):
        fstabstr = "# IMPORTANT : this default file uses drive paths for now, but UUID or LABEL should be used instead"
        
        for partition in self.partitions:
            drive = partition['drive']
            mountpoint = partition['mountpoint']
            filesystem = partition['filesystem']
            
            # FIXME use config
            options = "defaults,noatime"
            dump = "0" # gentoo handbook says this can stay 0
            fsck = "2" # good default except for / and partitions like swap
            
            if mountpoint == "/":
                fsck = "1"
            elif mountpoint == "":
                fsck = "0"
                mountpoint = "none"
            
            fstabline = f"{drive}\t{mountpoint}\t{filesystem}\t{options}\t{dump} {fsck}"
            fstabstr = f"{fstabstr}\n{fstabline}"
        
        return fstabstr
            