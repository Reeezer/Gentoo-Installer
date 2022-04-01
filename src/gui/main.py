import sys
from PyQt5.QtGui import QFont

from widget import *


def main():
    app = QApplication(sys.argv)
    
    sansFont = QFont("Bahnschrift", 10)
    app.setFont(sansFont)
    
    window = Window()
    window.setWindowTitle("Gentoo installer")
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
