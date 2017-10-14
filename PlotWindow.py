from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
import numpy as np
from SyntheticImage import SyntheticImage

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class PlotWindow(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        self.figure = Figure(facecolor='black')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.image = SyntheticImage(self.figure, self.canvas)
        self.ax = None
        self.setWindowTitle('Synthetic synchrotron image')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def drawSafe(self):
        try:
            self.canvas.draw()
        except RuntimeError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(e.strerror)
            msg.setWindowTitle('Runtime Error')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
    
    def plotImage(self):
        self.image.assembleImage()
        self.drawSafe()

    def set_colormax(self, intmax=1):
        self.image.changeIntensity(intmax)

    def savePlot(self, imageData, filename, cmname=None,
                 intmin=0, intmax=1, colorbar=False):
        pass
        """
        fig = False
        if len(self.captions) == 0:
            fig = Figure(figsize=(1,1))
        else:
            sz = self.figure.get_size_inches()
            minsz = min(sz)
            fig = Figure(figsize=(minsz,minsz))

        canvas = FigureCanvas(fig)
        ax, image = self.genImage(fig, imageData, cmname, intmin,
                                  intmax, colorbar)
        self.drawCaptions(fig=fig, ax=ax)

        ax.margins(0,0)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.get_xaxis().set_major_locator(matplotlib.ticker.NullLocator())
        ax.get_yaxis().set_major_locator(matplotlib.ticker.NullLocator())
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)

        canvas.print_figure(filename, dpi=len(imageData[0]))
        """

    def setSyntheticImage(self, image):
        self.image = image

    def syntheticImageUpdated(self):
        self.drawSafe()

