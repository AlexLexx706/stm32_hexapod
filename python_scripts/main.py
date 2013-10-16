# -*- coding: utf-8 -*-
import sys

from PyQt4 import QtGui, uic, QtCore
from mainwindow import MainWindow

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())  