from abc import abstractmethod
from turtle import left

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer, QObject
from api import get_mirrors
from PyQt5.QtGui import QIcon
from timezone import timezones

fileInstallerConf = None
fileDiskConf = None

from generate_conf import ConfigGenerator
from styles import styles

class Preference(QWidget):
    def __init__(self, title: str, layout: QLayout = None):
        super().__init__()
        self.layout = layout
        self.title = title
        self.setFixedWidth(300)
        self.setLayout(layout)

        self.addWidget(QLabel(title))

    def addWidget(self, widget:QWidget):
        if self.layout is None:
            super().addWidget(widget)
        else:
            self.layout.addWidget(widget)

    def getValue(self):
        print(self.title + "AbstractMethode")



class ComboPreference(Preference):
    def __init__(self, title:str, choices:list):
        super().__init__(title, QHBoxLayout())

        self.cbBox = QComboBox()
        [self.cbBox.addItem(choice) for choice in choices]

        self.addWidget(self.cbBox)

    def clear(self):
        self.cbBox.clear()

    def addItem(self, text, data=None):
        self.cbBox.addItem(text)
        self.cbBox.setItemData(self.cbBox.count() - 1, data)

    def connectChange(self, slot):
        self.cbBox.currentIndexChanged.connect(slot)

    def getValue(self):
        return self.cbBox.currentText()


class TextPreference(Preference):
    def __init__(self, title: str, default: str = ""):
        super().__init__(title, QHBoxLayout())

        self.lineEdit = QLineEdit()
        self.lineEdit.setText(default)
        self.addWidget(self.lineEdit)

        self.lineEdit.setFixedWidth(200)

    def getValue(self):
        return self.lineEdit.text()


class IntPreference(Preference):
    def __init__(self, title:str, suffix='', max=999999999):
        super().__init__(title, QHBoxLayout())

        self.spinbox = QSpinBox()
        self.spinbox.setSuffix(suffix)
        self.spinbox.setMaximum(max)
        self.addWidget(self.spinbox)

    def getValue(self):
        return self.spinbox.value()


class CheckPreference(Preference):
    def __init__(self, title:str):
        super().__init__(title, QHBoxLayout())

        self.checkbox = QCheckBox()
        self.addWidget(self.checkbox)

    def getValue(self):
        return self.checkbox.isChecked()




class Category(QListWidgetItem):
    def __init__(self, title:str, layout: QLayout = None, iconPath: str = ""):
        QListWidgetItem.__init__(self, title)
        self.setIcon(QIcon(iconPath))
        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.widget.setObjectName("category")
        self.title = title
        self.layout = layout

    def export(self):
        raise NotImplementedError

    def addWidget(self, widget: QWidget):
        if self.layout is None:
            self.widget.addWidget(widget)
        else:
            self.layout.addWidget(widget)


class LocalisationCategory(Category):
    def __init__(self, title):
        super().__init__(title, QVBoxLayout(), r".\images\localisation.png")
        self.langCombo = ComboPreference("Language (unused)", ["fr_FR.UTF-8", "de_DE.UTF-8", "en_US.UTF-8"])
        self.keyboardCombo = ComboPreference("Keyboard (unused)", ["fr", "azerty"])
        self.timeZoneCombo = ComboPreference("TimeZone", timezones)

        self.addWidget(self.langCombo)
        self.addWidget(self.keyboardCombo)
        self.addWidget(self.timeZoneCombo)

    def export(self):
        lang = self.langCombo.getValue()
        keyboard = self.keyboardCombo.getValue()
        conf = ConfigGenerator(fileInstallerConf, 'locale', {'lang':lang, 'keyboard':keyboard})
        conf.generate()
        timezone = self.timeZoneCombo.getValue()
        conf = ConfigGenerator(fileInstallerConf, 'timezone', {'timezone': timezone})
        conf.generate()

class PartitionWidget(Preference):
    def __init__(self, title):
        super().__init__(title, QVBoxLayout())

        self.namePref = TextPreference("Name")
        self.sizePref = IntPreference("Size", suffix=" MiB")
        self.mountPointPref = TextPreference("Mount point")
        self.fileSystemPref = ComboPreference("File system", ["","btrfs", "ext4", "f2f", "jfs", "reiserfs", "xfs", "vfat", "ntfs", "swap"]) #
        self.bootablePref = CheckPreference("Bootable")
        self.biosbootPref = CheckPreference("BiosBoot")

        btnDelete = QPushButton("Supprimer")
        btnDelete.clicked.connect(self.delete)

        self.addWidget(self.namePref)
        self.addWidget(self.sizePref)
        self.addWidget(self.mountPointPref)
        self.addWidget(self.fileSystemPref)
        self.addWidget(self.bootablePref)
        self.addWidget(self.biosbootPref)
        self.addWidget(btnDelete)

    def delete(self):
        self.setParent(None)

    def export(self):
        name = self.namePref.getValue()
        size = self.sizePref.getValue()
        mountpoint = self.mountPointPref.getValue()
        filesystem = self.fileSystemPref.getValue()
        bootable = self.bootablePref.getValue()

        attributes = {}
        if size > 0:
            attributes['size'] = size
        if bootable:
            attributes['bootable'] = int(bootable)
        if len(mountpoint) > 0:
            attributes['mountpoint'] = mountpoint
        if len(filesystem) > 0:
            attributes['filesystem'] = filesystem

        conf = ConfigGenerator(fileDiskConf, name, attributes)
        conf.generate()


class PartitionCategory(Category):
    def __init__(self, title):
        super().__init__(title, QVBoxLayout(), r".\images\partition.png")

        btnAdd = QPushButton("Add")
        btnAdd.clicked.connect(self.addPartition)

        self.generalSizePref = IntPreference("Size", suffix=" MiB")
        self.generalDrivePref = TextPreference("Drive")
        self.generalLabelPref = ComboPreference("Label", ["gpt", "dos"])

        self.addWidget(self.generalSizePref)
        self.addWidget(self.generalDrivePref)
        self.addWidget(self.generalLabelPref)
        self.addWidget(btnAdd)

        self.partitionsLayout = QHBoxLayout()

        widget = QWidget()
        widget.setLayout(self.partitionsLayout)

        scrollArea = QScrollArea()
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(widget)
        self.addWidget(scrollArea)


    def addPartition(self):
        partition = PartitionWidget(f"partition")
        self.partitionsLayout.addWidget(partition)

    def export(self):
        size = self.generalSizePref.spinbox.value()
        drive = self.generalDrivePref.lineEdit.text()

        conf = ConfigGenerator(fileDiskConf, 'general', {'size': size, 'drive': drive})
        conf.generate()

        for i in range(self.partitionsLayout.count()):
            self.partitionsLayout.itemAt(i).widget().export()



class MirrorsCategory(Category):
    def __init__(self, title):
        super().__init__(title, QVBoxLayout(), r".\images\mirror.png")

        self.RegionPreference = ComboPreference("Region :", [])
        self.CountryPreference = ComboPreference("Country :", [])
        self.MirrorPreference = ComboPreference("Mirror :", [])
        self.listUri = QListWidget()

        for region in get_mirrors():
            self.RegionPreference.addItem(region.name, region)

        self.RegionPreference.cbBox.setCurrentIndex(-1)
        self.RegionPreference.connectChange(self.changeRegion)
        self.CountryPreference.connectChange(self.changeCountry)
        self.MirrorPreference.connectChange(self.changeMirror)

        self.addWidget(self.RegionPreference)
        self.addWidget(self.CountryPreference)
        self.addWidget(self.MirrorPreference)
        self.addWidget(self.listUri)

    def changeRegion(self, index):
        if index == -1: return
        self.CountryPreference.clear()
        countries = self.RegionPreference.cbBox.itemData(index).countries
        for country in countries:
            self.CountryPreference.addItem(country.name, country)
        self.CountryPreference.cbBox.setCurrentIndex(-1)
        self.CountryPreference.cbBox.setCurrentIndex(0)

    def changeCountry(self, index):
        if index == -1: return
        self.MirrorPreference.clear()
        if self.CountryPreference.cbBox.itemData(index) is None:
            return
        mirrors = self.CountryPreference.cbBox.itemData(index).mirrors
        if mirrors is not None:
            for mirror in mirrors:
                self.MirrorPreference.addItem(mirror.name, mirror)
        self.MirrorPreference.cbBox.setCurrentIndex(-1)
        self.MirrorPreference.cbBox.setCurrentIndex(0)

    def changeMirror(self, index):
        if index == -1: return
        self.listUri.clear()
        if self.MirrorPreference.cbBox.itemData(index) is None:
            return
        uris = self.MirrorPreference.cbBox.itemData(index).uris
        if uris is not None:
            for uri in uris:
                self.listUri.addItem(uri)

    def export(self):
        urlItem = self.listUri.currentItem()
        if urlItem is not None:
            url = self.listUri.currentItem().text()
        else:
            url = 'None'
        conf = ConfigGenerator(fileInstallerConf, 'mirror', {'url':url})
        conf.generate()


class KernelCategory(Category):
    def __init__(self, title):
        super().__init__(title, QVBoxLayout(), r".\images\kernel.png")
        self.configPreference = ComboPreference("Config :", ["distkernel"])
        self.distkernelPreference =  ComboPreference("DistKernel :", ["gentoo-kernel-bin", "gentoo-kernel"])

        self.addWidget(self.configPreference)
        self.addWidget(self.distkernelPreference)

    def export(self):
        config = self.configPreference.cbBox.currentText()
        distkernel = self.distkernelPreference.cbBox.currentText()
        conf = ConfigGenerator(fileInstallerConf, 'kernel', {'config': config, 'distkernel': distkernel})
        conf.generate()


class SystemCategory(Category):
    def __init__(self, title):
        super().__init__(title, QVBoxLayout(), r".\images\system.png")

        self.hostnamePreference = TextPreference("Hostname")
        self.loggerPreference =  ComboPreference("Logger :", ["sysklogd", "syslog-ng", "metalog"])
        self.cronPreference = ComboPreference("Cron :", ["bcron", "dcron", "fcron", "cronie"])
        self.initSystemPref = ComboPreference("Init system", ["openrc", "systemd"])
        self.archPref = ComboPreference("ARCH", ["amd64", "amd32"])
        self.profilePref = TextPreference("profile", "default/linux/amd64/17.1")

        self.addWidget(self.hostnamePreference)
        self.addWidget(self.loggerPreference)
        self.addWidget(self.cronPreference)
        self.addWidget(self.initSystemPref)
        self.addWidget(self.archPref)
        self.addWidget(self.profilePref)

    def export(self):
        hostname = self.hostnamePreference.getValue()
        logger = self.loggerPreference.getValue()
        cron = self.cronPreference.getValue()
        arch = self.archPref.getValue()

        initsystem = self.initSystemPref.getValue()
        profile = self.profilePref.getValue()

        conf = ConfigGenerator(fileInstallerConf, 'system', {'hostname': hostname, 'logger': logger, 'cron': cron})
        conf.generate()

        conf1 = ConfigGenerator(fileInstallerConf, 'gentoo', {'arch': arch, 'initsystem': initsystem})
        conf1.generate()

        conf2 = ConfigGenerator(fileInstallerConf, 'portage', {'profile': profile})
        conf2.generate()

class BootCategory(Category):
    def __init__(self, title):
        super().__init__(title, QVBoxLayout(), r".\images\boot.png")

        self.modePreference =  ComboPreference("Mode :", ["bios", "efi"])
        self.bootloaderPreference = ComboPreference("Bootloader :", ["grub", "lilo", "efibootmgr"])

        self.addWidget(self.modePreference)
        self.addWidget(self.bootloaderPreference)

    def export(self):
        mode = self.modePreference.getValue()
        bootloader = self.bootloaderPreference.getValue()
        conf = ConfigGenerator(fileInstallerConf, 'boot', {'mode': mode, 'bootloader': bootloader})
        conf.generate()

class SideBar(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.setIconSize(QSize(30,30))
        self.addItem(LocalisationCategory("Localisation"))
        self.addItem(PartitionCategory("Partitions"))
        self.addItem(MirrorsCategory("Mirroirs"))
        self.addItem(KernelCategory("Kernel"))
        self.addItem(SystemCategory("System"))
        self.addItem(BootCategory("Boot"))


        self.setFixedWidth(140)

    def export(self):
        global fileInstallerConf, fileDiskConf
        fileInstallerConf = open("installer/installer.conf", 'w')
        fileDiskConf = open("installer/disks.conf", 'w')
        for i in range(self.count()):
            self.item(i).export()
        fileInstallerConf.close()
        fileDiskConf.close()

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        mainLayout = QHBoxLayout()

        self.sidebar = SideBar()
        self.sidebar.itemSelectionChanged.connect(self.changeMainWidget)

        self.preferencesLayout = QVBoxLayout()

        self.btnExport = QPushButton("Export")
        self.btnExport.clicked.connect(self.sidebar.export)
        self.btnExport.clicked.connect(self.export)
        self.btnExport.setFixedWidth(140)

        # verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.message = QLabel()

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.sidebar)
        #leftLayout.addStretch()
        leftLayout.addWidget(self.message)
        leftLayout.addWidget(self.btnExport)

        leftPane = QWidget()
        leftPane.setLayout(leftLayout)
        leftPane.setObjectName("leftPane")
        leftPane.setFixedWidth(160)

        mainLayout.addWidget(leftPane)
        mainLayout.addLayout(self.preferencesLayout)

        self.setLayout(mainLayout)

        self.resize(500, 400)

        self.setStyleSheet(styles)

    def removeMessage(self):
        self.message.setText("")

    def export(self):
        self.message.setText("Exported")
        QTimer.singleShot(5000, self.removeMessage)

    def changeMainWidget(self):
        for i in reversed(range(self.preferencesLayout.count())):
            self.preferencesLayout.itemAt(i).widget().setParent(None)
        self.preferencesLayout.addWidget(self.sidebar.selectedItems()[0].widget)








