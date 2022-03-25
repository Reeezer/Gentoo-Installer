import sys

from widget import *


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("Installateur Gentoo")
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
