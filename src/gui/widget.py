from abc import abstractmethod
from turtle import left

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer
from api import get_mirrors

from generate_conf import ConfigGenerator
from styles import styles

class Preference(QWidget):
    def __init__(self, title:str):
        QWidget.__init__(self)
        self.title = title
        self.setFixedWidth(300)

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
        
        self.lineEdit.setFixedWidth(200)
        
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
        self.widget.setObjectName("category")    
        self.title = title
        
    def export(self):
        print(self.title)


class LocalisationCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        self.langCombo = ComboPreference("Language", ["fr_FR.UTF-8", "de_DE.UTF-8", "en_US.UTF-8"])
        self.keyboardCombo = ComboPreference("Keyboard", ["fr", "azerty"])
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
        widget = QWidget()
        
        self.label = QLabel(title)
        self.startPref = IntPreference("Start")
        self.sizePref = IntPreference("Size")
        self.mountPointPref = TextPreference("Mount point")
        self.fileSystemPref = TextPreference("File system")
        self.bootablePref = CheckPreference("Bootable")

        layout.addWidget(self.label)
        layout.addWidget(self.startPref)
        layout.addWidget(self.sizePref)
        layout.addWidget(self.mountPointPref)
        layout.addWidget(self.fileSystemPref)
        layout.addWidget(self.bootablePref)
        
        self.setLayout(layout)

class PartitionCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        layout = QVBoxLayout()
        self.partitions = []

        btnAdd = QPushButton("Add")
        btnAdd.clicked.connect(self.addPartition)
        btnDelete = QPushButton("Remove")
        btnDelete.clicked.connect(self.deletePartition)
        
        self.generalSizePref = IntPreference("Size")
        self.generalDrivePref = TextPreference("Drive")
        self.generalLabelPref = ComboPreference("Label", ["gpt", "dos"])

        layout.addWidget(self.generalSizePref)
        layout.addWidget(self.generalDrivePref)
        layout.addWidget(self.generalLabelPref)
        layout.addWidget(btnAdd)
        layout.addWidget(btnDelete)
        
        self.partitionsLayout = QVBoxLayout()
        
        widget = QWidget()
        widget.setLayout(self.partitionsLayout)
        
        scrollArea = QScrollArea()
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(widget)
        scrollArea.setFixedWidth(400)
        layout.addWidget(scrollArea)
        
        self.widget.setLayout(layout)

    def addPartition(self):
        partition = PartitionWidget(f"Partition {len(self.partitions)}")
        self.partitions.append(partition)
        self.partitionsLayout.addWidget(partition)

    def deletePartition(self):
        self.partitions[-1].setParent(None)
        self.partitions.pop(-1)
        
    def export(self):
        super().export()
        file = open('installer/partitions.conf', 'w')
        confs = list()
        
        # General 
        size = self.generalSizePref.spinbox.value()
        drive = self.generalDrivePref.lineEdit.text()
        label = self.generalLabelPref.cbBox.currentText()
        confs.append(ConfigGenerator(file, 'general', {'size':size, 'label':label, 'drive': drive}))
        
        # Each partition
        i = 0
        for partition in self.partitions:
            start = partition.startPref.spinbox.value()
            size = partition.sizePref.spinbox.value()
            mountpoint = partition.mountPointPref.lineEdit.text()
            filesystem = partition.fileSystemPref.lineEdit.text()
            bootable = partition.bootablePref.checkbox.isChecked()
            
            attributes = dict()
            if start > 0:
                attributes['start'] = start
            if size > 0:
                attributes['size'] = size
            if bootable:
                attributes['bootable'] = bootable
            attributes['mountpoint'] = mountpoint
            attributes['filesystem'] = filesystem
            confs.append(ConfigGenerator(file, f"partition{i}", attributes))
            i += 1
        
        [conf.generate() for conf in confs]


class InitSystemCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        
        self.initSystemPref = ComboPreference("Init system", ["openrc", "systemd"])
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

        layout.addWidget(LargeTextPreference("Use Flags"))
        urlLink = "<a href=\"https://www.gentoo.org/support/use-flags/\">See available use flags</a>"
        label = QLabel(urlLink)
        label.setOpenExternalLinks(True)
        layout.addWidget(label)

        self.widget.setLayout(layout)


class SideBar(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.addItem(LocalisationCategory("Localisation"))
        self.addItem(PartitionCategory("Partitions"))
        self.addItem(InitSystemCategory("Init sytem"))
        self.addItem(MirrorsCategory("Mirrors"))
        self.addItem(UseFlagCategory("Use flags"))
        
        self.setFixedWidth(140)

    def export(self):
        for i in range(self.count()):
            self.item(i).export()

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
        leftLayout.addStretch()
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