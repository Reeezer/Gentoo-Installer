class ConfigGenerator:
    def __init__(self, file, title, attributes):
        self.title = title
        self.file = file
        self.attributes = attributes
    
    def generate(self):
        print(f"[{self.title}]", file=self.file)
        for key, value in self.attributes.items():
            print(f"{key}={value}", file=self.file)
        print('', file=self.file)
        
if __name__ == '__main__':
    file1 = open('log1.conf', 'w')
    file2 = open('log2.conf', 'w')
    
    confs = list()
    
    confs.append(ConfigGenerator(file1, 'gentoo', {'arch':'amd64', 'initsystem':'openrc'}))
    confs.append(ConfigGenerator(file1, 'drive', {'drive':'/dev/sda', 'size':'32768', 'label':'gpt'}))
    confs.append(ConfigGenerator(file1, 'mirror', {'url':'https://mirror.init7.net'}))
    confs.append(ConfigGenerator(file1, 'portage', {'profile':'default/linux/amd64/17.1'}))
    confs.append(ConfigGenerator(file1, 'timezone', {'profile':'Europe/Zurich'}))
    confs.append(ConfigGenerator(file1, 'kernel', {'config':'distkernel', 'distkernel':'gentoo-kernel-bin'}))
    
    confs.append(ConfigGenerator(file2, 'general', {'unit':'MiB', 'drive':'/dev/sda'}))
    confs.append(ConfigGenerator(file2, 'boot', {'start':'2', 'size':'200', 'mountpoint':'/boot', 'filesystem':'ext2'}))
    confs.append(ConfigGenerator(file2, 'root', {'size':'8192', 'mountpoint':'/', 'filesystem':'ext2'}))
    confs.append(ConfigGenerator(file2, 'home', {'mountpoint':'/home', 'filesystem':'ext2'}))
    
    [conf.generate() for conf in confs]