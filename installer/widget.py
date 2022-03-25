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

    def clear(self):
        self.cbBox.clear()

    def addItem(self, text, data=None):
        self.cbBox.addItem(text)
        self.cbBox.setItemData(self.cbBox.count() - 1, data)


class TextPreference(Preference):
    def __init__(self, title:str):
        Preference.__init__(self, title)
        layout = QHBoxLayout()
        self.lineEdit = QLineEdit()

        layout.addWidget(QLabel(title))
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)

class IntPreference(Preference):
    def __init__(self, title:str):
        Preference.__init__(self, title)
        layout = QHBoxLayout()
        self.spinbox = QSpinBox()

        layout.addWidget(QLabel(title))
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

class CheckPreference(Preference):
    def __init__(self, title:str):
        Preference.__init__(self, title)
        layout = QHBoxLayout()
        self.checkbox = QCheckBox()

        layout.addWidget(QLabel(title))
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

        layout.addWidget(QLabel(title))
        layout.addWidget(TextPreference("Start"))
        layout.addWidget(IntPreference("Size"))
        layout.addWidget(TextPreference("Mount point"))
        layout.addWidget(TextPreference("File system"))
        layout.addWidget(CheckPreference("Bootable"))
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

        layout.addWidget(IntPreference("Size"))
        layout.addWidget(TextPreference("Drive"))
        layout.addWidget(ComboPreference("Label", ["gpt", "dos"]))
        layout.addWidget(btnAdd)
        layout.addWidget(btnDelete)
        self.partitionsLayout = QHBoxLayout()
        layout.addLayout(self.partitionsLayout)
        self.widget.setLayout(layout)

    def addPartition(self):
        partition = PartitionWidget(f"Parition {len(self.partitions)}")
        self.partitions.append(partition)
        self.partitionsLayout.addWidget(partition)

    def deletePartition(self):
        self.partitions[-1].setParent(None)
        self.partitions.pop(-1)
        print(self.partitions)


class InitSystemCategory(Category):
    def __init__(self, title):
        Category.__init__(self, title)
        layout = QVBoxLayout()

        layout.addWidget(ComboPreference("Système d'amorçage", ["OpenRC", "Systemd"]))

        self.widget.setLayout(layout)


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




