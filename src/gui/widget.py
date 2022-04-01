from abc import abstractmethod

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl, QObject
from api import get_mirrors

from generate_conf import ConfigGenerator


class Preference(QWidget):
    def __init__(self, title:str):
        QWidget.__init__(self)
        self.title = title


class ComboPreference(Preference):
    def __init__(self, title:str, choices:list):
        Preference.__init__(self, title)
        
        self.cbBox = QComboBox()
        [self.cbBox.addItem(choice) for choice in choices]
        
        label = QLabel(title)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.cbBox)
        
        self.setLayout(layout)

    def clear(self):
        self.cbBox.clear()

    def addItem(self, text, data=None):
        self.cbBox.addItem(text)
        self.cbBox.setItemData(self.cbBox.count() - 1, data)


class TextPreference(Preference):
    def __init__(self, title:str):
        Preference.__init__(self, title)
        
        self.lineEdit = QLineEdit()
        label = QLabel(title)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.lineEdit)
        
        self.setLayout(layout)


class LargeTextPreference(Preference):
    def __init__(self, title: str):
        Preference.__init__(self, title)

        self.textEdit = QTextEdit()
        label = QLabel(title)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.textEdit)

        self.setLayout(layout)

class IntPreference(Preference):
    def __init__(self, title:str):
        Preference.__init__(self, title)
        
        self.spinbox = QSpinBox()
        label = QLabel(title)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.spinbox)
        
        self.setLayout(layout)

class CheckPreference(Preference):
    def __init__(self, title:str):
        Preference.__init__(self, title)
        
        self.checkbox = QCheckBox()
        label = QLabel(title)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.checkbox)
        
        self.setLayout(layout)




class Category(QListWidgetItem):
    def __init__(self, title:str):
        QListWidgetItem.__init__(self, title)
        self.widget = QWidget()
        self.title = title
        
    def export(self):
        print(self.title)


class LocalisationCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        self.langCombo = ComboPreference("Langue", ["fr_FR.UTF-8", "de_DE.UTF-8", "en_US.UTF-8"])
        self.keyboardCombo = ComboPreference("Clavier", ["fr", "azerty"])
        self.timeZoneCombo = ComboPreference("TimeZone", ["Europe/Berlin", "Europe/Londres"])
        
        layout = QVBoxLayout()
        layout.addWidget(self.langCombo)
        layout.addWidget(self.keyboardCombo)
        layout.addWidget(self.timeZoneCombo)
        self.widget.setLayout(layout)
        
    def export(self):
        super().export()
        file = open('installer/localisation.conf', 'w')
        
        lang = self.langCombo.cbBox.currentText()
        keyboard = self.keyboardCombo.cbBox.currentText()
        conf = ConfigGenerator(file, 'locale', {'lang':lang, 'keyboard':keyboard})
        conf.generate()
        timezone = self.timeZoneCombo.cbBox.currentText()
        conf = ConfigGenerator(file, 'timezone', {'timezone': timezone})
        conf.generate()

class PartitionWidget(Preference):
    def __init__(self, title):
        Preference.__init__(self, title)
        layout = QVBoxLayout()
        
        self.namePref = TextPreference("Name")
        self.sizePref = IntPreference("Size")
        self.mountPointPref = TextPreference("Mount point")
        self.fileSystemPref = ComboPreference("File system", ["btrfs", "ext4", "f2f", "jfs", "reiserfs", "xfs", "vfat", "ntfs", "swap"]) #
        self.bootablePref = CheckPreference("Bootable")
        self.biosbootPref = CheckPreference("BiosBoot")

        layout.addWidget(self.namePref)
        layout.addWidget(self.sizePref)
        layout.addWidget(self.mountPointPref)
        layout.addWidget(self.fileSystemPref)
        layout.addWidget(self.bootablePref)
        layout.addWidget(self.biosbootPref)
        
        self.setLayout(layout)

        self.setParent(None)

        btnDelete = QPushButton("Supprimer")
        btnDelete.clicked.connect(self.delete)
        layout.addWidget(btnDelete)

    def delete(self):
        self.setParent(None)

    def export(self):
        name = self.namePref.lineEdit.text()
        size = self.sizePref.spinbox.value()
        mountpoint = self.mountPointPref.lineEdit.text()
        filesystem = self.fileSystemPref.cbBox.currentText()
        bootable = self.bootablePref.checkbox.isChecked()

        attributes = {}
        attributes['name'] = name
        if size > 0:
            attributes['size'] = size
        if bootable:
            attributes['bootable'] = bootable
        attributes['mountpoint'] = mountpoint
        attributes['filesystem'] = filesystem

        file = open('installer/partitions.conf', 'a')
        conf = ConfigGenerator(file, name, attributes)
        conf.generate()


class PartitionCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        layout = QVBoxLayout()

        btnAdd = QPushButton("Ajouter")
        btnAdd.clicked.connect(self.addPartition)
        
        self.generalSizePref = IntPreference("Size")
        self.generalDrivePref = TextPreference("Drive")
        self.generalLabelPref = ComboPreference("Label", ["gpt", "dos"])

        layout.addWidget(self.generalSizePref)
        layout.addWidget(self.generalDrivePref)
        layout.addWidget(self.generalLabelPref)
        layout.addWidget(btnAdd)
        
        self.partitionsLayout = QHBoxLayout()
        layout.addLayout(self.partitionsLayout)
        
        self.widget.setLayout(layout)

    def addPartition(self):
        partition = PartitionWidget(f"partition")
        self.partitionsLayout.addWidget(partition)

    def export(self):
        super().export()
        size = self.generalSizePref.spinbox.value()
        drive = self.generalDrivePref.lineEdit.text()

        file = open('installer/partitions.conf', 'w')
        conf = ConfigGenerator(file, 'general', {'size': size, 'drive': drive})
        conf.generate()
        file.close()

        for i in range(self.partitionsLayout.count()):
            self.partitionsLayout.itemAt(i).widget().export()


class InitSystemCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        
        self.initSystemPref = ComboPreference("Système d'amorçage", ["openrc", "systemd"])
        self.archPref = ComboPreference("ARCH", ["amd64", "amd32"])

        layout = QVBoxLayout()
        layout.addWidget(self.initSystemPref)
        layout.addWidget(self.archPref)
        self.widget.setLayout(layout)

    def export(self):
        super().export()
        file = open('installer/initsystem.conf', 'w')
        
        arch = self.archPref.cbBox.currentText()
        initsystem = self.initSystemPref.cbBox.currentText()
        conf = ConfigGenerator(file, 'gentoo', {'arch':arch, 'initsystem':initsystem})
        conf.generate()

class MirrorsCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        layout = QVBoxLayout()

        self.RegionPreference = ComboPreference("Region :", [])
        self.CountryPreference = ComboPreference("Country :", [])
        self.MirrorPreference = ComboPreference("Mirror :", [])
        self.listUri = QListWidget()

        for region in get_mirrors():
            self.RegionPreference.cbBox.addItem(region.name)
            self.RegionPreference.cbBox.setItemData(self.RegionPreference.cbBox.count() - 1, region)

        self.RegionPreference.cbBox.currentIndexChanged.connect(self.changeRegion)
        self.CountryPreference.cbBox.currentIndexChanged.connect(self.changeCountry)
        self.MirrorPreference.cbBox.currentIndexChanged.connect(self.changeMirror)

        layout.addWidget(self.RegionPreference)
        layout.addWidget(self.CountryPreference)
        layout.addWidget(self.MirrorPreference)
        layout.addWidget(self.listUri)

        self.widget.setLayout(layout)

    def changeRegion(self, index):
        self.CountryPreference.clear()
        countries = self.RegionPreference.cbBox.itemData(index).countries
        for country in countries:
            self.CountryPreference.addItem(country.name, country)
        self.CountryPreference.cbBox.setCurrentIndex(-1)
        self.CountryPreference.cbBox.setCurrentIndex(0)

    def changeCountry(self, index):
        self.MirrorPreference.clear()
        if self.CountryPreference.cbBox.itemData(index) == None:
            return
        mirrors = self.CountryPreference.cbBox.itemData(index).mirrors
        if mirrors is not None:
            for mirror in mirrors:
                self.MirrorPreference.addItem(mirror.name, mirror)
        self.MirrorPreference.cbBox.setCurrentIndex(-1)
        self.MirrorPreference.cbBox.setCurrentIndex(0)

    def changeMirror(self, index):
        self.listUri.clear()
        if self.MirrorPreference.cbBox.itemData(index) == None:
            return
        uris = self.MirrorPreference.cbBox.itemData(index).uris
        if uris is not None:
            for uri in uris:
                self.listUri.addItem(uri)

    def export(self):
        super().export()
        file = open('installer/mirrors.conf', 'w')
        
        urlItem = self.listUri.currentItem()
        if urlItem is not None:
            url = self.listUri.currentItem().text()
        else:
            url = 'None'
        conf = ConfigGenerator(file, 'mirror', {'url':url})
        conf.generate()


class UseFlagCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        layout = QVBoxLayout()

        layout.addWidget(LargeTextPreference("Use Falgs"))
        urlLink = "<a href=\"https://www.gentoo.org/support/use-flags/\">See use flags available</a>"
        label = QLabel(urlLink)
        label.setOpenExternalLinks(True)
        layout.addWidget(label)

        self.widget.setLayout(layout)


class SideBar(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.addItem(LocalisationCategory("Localisation"))
        self.addItem(PartitionCategory("Partitions"))
        self.addItem(InitSystemCategory("Système d'amorçage"))
        self.addItem(MirrorsCategory("Mirroirs"))
        self.addItem(UseFlagCategory("Use flags"))

    def export(self):
        for i in range(self.count()):
            self.item(i).export()


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        mainLayout = QHBoxLayout()

        self.sidebar = SideBar()
        self.preferencesLayout = QVBoxLayout()
        
        btnExport = QPushButton("Exporter")
        btnExport.clicked.connect(self.sidebar.export)
        
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.sidebar)
        leftLayout.addWidget(btnExport)

        self.sidebar.itemSelectionChanged.connect(self.changeMainWidget)

        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(self.preferencesLayout)
        
        self.setLayout(mainLayout)

    def changeMainWidget(self):
        for i in reversed(range(self.preferencesLayout.count())):
            self.preferencesLayout.itemAt(i).widget().setParent(None)
        self.preferencesLayout.addWidget(self.sidebar.selectedItems()[0].widget)



# config --> kconfig, genkernel, distkernel
# distkernel --> gentoo-kernel gentoo-kernel-bin


# locker --> sysklogd, syslog-ng, metalog
# cron --> bcron dcron fcron cronie

# mode --> bios efi
# bootloader --> grub, lilo, efibootmgr
