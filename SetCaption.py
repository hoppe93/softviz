from PyQt5 import QtWidgets
from ui import setcaption_design
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib

from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class SetCaption(QtWidgets.QDialog):
    captionsUpdated = pyqtSignal(list)

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = setcaption_design.Ui_SetCaption()
        self.ui.setupUi(self)
        self.currentCaptions = list()

        self.ui.tblCaptions.setHorizontalHeaderLabels(['X', 'Y', 'Fontsize', 'Caption text'])
        header = self.ui.tblCaptions.horizontalHeader()
        header.resizeSection(0, 70)
        header.resizeSection(1, 70)
        header.resizeSection(1, 100)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.ui.tblCaptions.setItem(0, 0, QTableWidgetItem('0'))
        self.ui.tblCaptions.setItem(0, 1, QTableWidgetItem('0'))
        self.ui.tblCaptions.setItem(0, 2, QTableWidgetItem('12'))
        self.ui.tblCaptions.setItem(0, 3, QTableWidgetItem(''))

        self.bindEvents()

    def bindEvents(self):
        self.ui.btnAddCaption.clicked.connect(self.addEmptyCaption)
        self.ui.tblCaptions.cellChanged.connect(self.updateCaption)

    def addEmptyCaption(self):
        i = self.ui.tblCaptions.rowCount()
        print(i)

        x = self.ui.tblCaptions.item(i-1, 0).text()
        y = self.ui.tblCaptions.item(i-1, 1).text()
        f = self.ui.tblCaptions.item(i-1, 2).text()
        self.addCaption(x, y, f, '')

    def addCaption(self, x, y, fontsize, caption):
        i = self.ui.tblCaptions.rowCount()
        self.ui.tblCaptions.setRowCount(i+1)

        self.ui.tblCaptions.setItem(i, 0, QTableWidgetItem(x))
        self.ui.tblCaptions.setItem(i, 1, QTableWidgetItem(y))
        self.ui.tblCaptions.setItem(i, 2, QTableWidgetItem(fontsize))
        self.ui.tblCaptions.setItem(i, 3, QTableWidgetItem(caption))

    def getCaptions(self):
        lst = list()
        for i in range(0, self.ui.tblCaptions.rowCount()):
            item = list()
            try:
                for j in range(0, self.ui.tblCaptions.columnCount()):
                    item.append(self.ui.tblCaptions.item(i, j).text())
            except (AttributeError, IndexError):
                continue

            if not self.is_float(item[0]) or not self.is_float(item[1]):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText('The X and Y coordinates must be floating point values.')
                msg.setWindowTitle('Error')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            if not self.is_int(item[2]):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText('The font size must be an integer.')
                msg.setWindowTitle('Error')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

            if item[-1] is not '':
                lst.append(item)

        return lst


    def is_float(self, n):
        try:
            float(n)
            return True
        except ValueError:
            return False

    def is_int(self, n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def updateCaption(self):
        lst = self.getCaptions()
        self.currentCaptions = lst
        self.captionsUpdated.emit(lst)

