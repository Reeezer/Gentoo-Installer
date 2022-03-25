from abc import abstractmethod

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
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

class TextPreference(Preference):
    def __init__(self, title:str):
        Preference.__init__(self, title)
        
        self.lineEdit = QLineEdit()
        label = QLabel(title)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.lineEdit)
        
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
        
        layout = QVBoxLayout()
        layout.addWidget(self.langCombo)
        layout.addWidget(self.keyboardCombo)
        self.widget.setLayout(layout)
        
    def export(self):
        super().export()
        file = open('installer/localisation.conf', 'w')
        
        lang = self.langCombo.cbBox.currentText()
        keyboard = self.keyboardCombo.cbBox.currentText()
        conf = ConfigGenerator(file, 'locale', {'lang':lang, 'keyboard':keyboard})
        
        conf.generate()

class PartitionWidget(Preference):
    def __init__(self, title):
        Preference.__init__(self, title)
        layout = QVBoxLayout()
        
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

        btnAdd = QPushButton("Ajouter")
        btnAdd.clicked.connect(self.addPartition)
        btnDelete = QPushButton("Supprimer")
        btnDelete.clicked.connect(self.deletePartition)
        
        self.generalSizePref = IntPreference("Size")
        self.generalDrivePref = TextPreference("Drive")
        self.generalLabelPref = ComboPreference("Label", ["gpt", "dos"])

        layout.addWidget(self.generalSizePref)
        layout.addWidget(self.generalDrivePref)
        layout.addWidget(self.generalLabelPref)
        layout.addWidget(btnAdd)
        layout.addWidget(btnDelete)
        
        self.partitionsLayout = QHBoxLayout()
        layout.addLayout(self.partitionsLayout)
        
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
        layout = QVBoxLayout()
        cb = QComboBox()
        cb.addItem("OpenRC")
        cb.addItem("Systemd")
        layout.addWidget(cb)

        self.widget.setLayout(layout)


class MirrorsCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        layout = QVBoxLayout()

        self.cbRegion = QComboBox()
        self.cbCountry = QComboBox()
        self.cbMirror = QComboBox()
        self.cbUrl = QListWidget()

        for region in get_mirrors():
            self.cbRegion.addItem(region.name)
            self.cbRegion.setItemData(self.cbRegion.count()-1, region)

        self.cbRegion.currentIndexChanged.connect(self.changeRegion)
        self.cbCountry.currentIndexChanged.connect(self.changeCountry)
        self.cbMirror.currentIndexChanged.connect(self.changeMirror)

        layout.addWidget(self.cbRegion)
        layout.addWidget(self.cbCountry)
        layout.addWidget(self.cbMirror)
        layout.addWidget(self.cbUrl)

        self.widget.setLayout(layout)

    def changeRegion(self, index):
        self.cbCountry.clear()
        countries = self.cbRegion.itemData(index).countries
        for country in countries:
            self.cbCountry.addItem(country.name)
            self.cbCountry.setItemData(self.cbCountry.count() - 1, country)
        self.cbCountry.setCurrentIndex(-1)
        self.cbCountry.setCurrentIndex(0)

    def changeCountry(self, index):
        self.cbMirror.clear()
        if self.cbCountry.itemData(index) == None:
            return
        mirrors = self.cbCountry.itemData(index).mirrors
        if mirrors is not None:
            for mirror in mirrors:
                self.cbMirror.addItem(mirror.name)
                self.cbMirror.setItemData(self.cbMirror.count() - 1, mirror)
        self.cbMirror.setCurrentIndex(-1)
        self.cbMirror.setCurrentIndex(0)

    def changeMirror(self, index):
        self.cbUrl.clear()
        if self.cbMirror.itemData(index) == None:
            return
        uris = self.cbMirror.itemData(index).uris
        if uris is not None:
            for uri in uris:
                self.cbUrl.addItem(uri)



class SideBar(QListWidget):
    def __init__(self):
        QListWidget.__init__(self)
        self.addItem(LocalisationCategory("Localisation"))
        self.addItem(PartitionCategory("Partitions"))
        self.addItem(InitSystemCategory("Système d'amorçage"))
        self.addItem(MirrorsCategory("Mirroirs"))

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




