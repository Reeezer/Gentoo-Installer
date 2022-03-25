from abc import abstractmethod

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from api import get_mirrors


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
        layout.addWidget(QLabel("name"))
        layout.addWidget(QLineEdit())
        layout.addWidget(QLabel("begin at"))
        layout.addWidget(QLineEdit())
        layout.addWidget(QLabel("size"))
        layout.addWidget(QLineEdit())
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




