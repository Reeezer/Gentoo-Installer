import sys
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon

from widget import *


def main():
    app = QApplication(sys.argv)
    
    sansFont = QFont("Bahnschrift", 10)
    app.setFont(sansFont)
    
    window = Window()
    window.setWindowTitle("Gentoo installer")
    window.setWindowIcon(QIcon('./images/icon.png'))
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
