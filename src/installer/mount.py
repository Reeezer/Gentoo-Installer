class Mount:
    """Helper to compute the mount order of partitions"""
    
    def __init__(self, partitions:list) -> None:
        self.partitions = partitions
    
    # maybe there's a smarter way, but if it works it aint stupid
    def sorted(self) -> list:
        """Returns a sorted list of partitions in the order they should be mounted in.
        The agorithm simply counts the amount of times the / character appears in the
        partition's mountpoint, the more the deeper it is mounted and so the later it
        should be mounted, to make sure its potential containing folder is already mounted.
        / is always mounted first since a trailing / is trimmed, making its 'depth' 0.
        The original partition objects are returned in the list.
        Partitions that don't have a mountpoint are ignored.
        """
        partslevels = {} # levels of partitions mount (0 = partitions to mount first, 1 = partitions to mount in second, 2 = ...)
        
        for partition in self.partitions:          
            mountpoint = partition['mountpoint']
            if mountpoint == '': # if there's no mountpoint they shouldn't be mounted
                continue
            
            mountpoint = mountpoint[:-1] if mountpoint[-1] == '/' else mountpoint # remove trailing slash
            slashcount = mountpoint.count('/') # only / should have 0 at this point making it the first in the list
            
            if slashcount in partslevels:
                partslevels[slashcount].append(partition)
            else:
                partslevels[slashcount] = [partition]
            
        # place all partitions in a list in the order they should be mounted in
        partslevelslist = []    
        for level in range(max(partslevels.keys()) + 1):
            if level in partslevels: # might skip a level, e.g. /boot/grub/efi
                for partition in partslevels[level]:
                    partslevelslist.append(partition)
        
        return partslevelslist
            
                  
            
            
            
        
        