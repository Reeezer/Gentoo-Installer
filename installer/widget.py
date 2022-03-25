from abc import abstractmethod

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from api import get_mirrors

from PyQt5.QtCore import pyqtSignal, pyqtSlot


class Preference(QWidget):
    def __init__(self, title:str):
        QWidget.__init__(self)
        self.title = title


class ComboPreference(Preference):
    def __init__(self, title:str, choices:list):
        Preference.__init__(self, title)
        layout = QHBoxLayout()
        self.cbBox = QComboBox()
        for choice in choices:
            self.cbBox.addItem(choice)

        layout.addWidget(QLabel(title))
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
        layout = QVBoxLayout()
        layout.addWidget(ComboPreference("Langue", ["Français", "Allemand"]))
        layout.addWidget(ComboPreference("Clavier", ["Français", "Allemand"]))
        self.widget.setLayout(layout)



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
        self.addItem(MirrorsCategory("Miroirs"))

    def export(self):
        for i in range(self.count()):
            self.item(i).export()


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QHBoxLayout()

        self.sidebar = SideBar()
        self.preferencesLayout = QVBoxLayout()

        self.sidebar.itemSelectionChanged.connect(self.changeMainWidget)

        layout.addWidget(self.sidebar)
        layout.addLayout(self.preferencesLayout)
        self.setLayout(layout)
        self.sidebar.export()

    def changeMainWidget(self):
        for i in reversed(range(self.preferencesLayout.count())):
            self.preferencesLayout.itemAt(i).widget().setParent(None)
        self.preferencesLayout.addWidget(self.sidebar.selectedItems()[0].widget)




