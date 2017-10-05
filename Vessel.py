from PyQt5 import QtWidgets
from ui import vessel_design
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib

from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtCore import pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class Vessel(QtWidgets.QDialog):
    overlayChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = vessel_design.Ui_Vessel()
        self.ui.setupUi(self)

        self.bindEvents()

    def bindEvents(self):
        self.ui.gbCrossSection.toggled.connect(self.emitReplot)
        self.ui.cbCSWall.stateChanged.connect(self.emitReplot)
        self.ui.cbCSSeparatrix.stateChanged.connect(self.emitReplot)
        self.ui.cbCSFlux.stateChanged.connect(self.emitReplot)

    def emitReplot(self):
        status = {
            'cs': {
                'wall': self.ui.cbCSWall.isChecked(),
                'separatrix': self.ui.cbCSSeparatrix.isChecked(),
                'flux': self.ui.cbCSFlux.isChecked()
            }
        }

        self.overlayChanged.emit(status)

