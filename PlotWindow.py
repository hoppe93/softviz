from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class PlotWindow(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        self.figure = Figure(facecolor='black')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.image = None
        self.ax = None
        self.captions = list()
        self.setWindowTitle('Synthetic synchrotron image')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def drawCaptions(self, fig, ax):
        for i in range(0, len(ax.texts)):
            ax.texts.remove(ax.texts[0])

        for item in self.captions:
            X, Y = float(item[0]), float(item[1])
            fontsize = int(item[2])
            caption = item[3]

            ax.text(X, Y, caption, color='white', fontsize=fontsize)

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

    def genImage(self, fig, imageData, cmname=None, intmin=0, intmax=1,
                  colorbar=False, relativeColorbar=False):
        colormap = plt.get_cmap(cmname)

        fig.clear()
        ax = fig.add_subplot(111)
        #ax.hold(False)
        image = ax.imshow(imageData, origin='lower', cmap=colormap,
                          interpolation=None, clim=(intmin, intmax))
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        ax.set_axis_off()
        #ax.set_facecolor('black')

        if colorbar:
            if relativeColorbar:
                mx = np.amax(imageData)
                cbar = fig.colorbar(image, shrink=0.8, ticks=[0,mx*0.2,mx*0.4,mx*0.6,mx*0.8,mx])
                cbar.ax.set_yticklabels(['0\%','20\%','40\%','60\%','80\%','100\%'])
            else:
                cbar = fig.colorbar(image, shrink=0.8)
            cbar.ax.tick_params(labelcolor='white', color='white')

        return ax, image

    def plotImage(self, imageData, cmname=None, intmin=0, intmax=1,
                  colorbar=False, relativeColorbar=False):
        self.ax, self.image = self.genImage(self.figure, imageData, cmname,
                                            intmin, intmax, colorbar, relativeColorbar)
        self.drawCaptions(self.figure, self.ax)
        self.drawSafe()

    def set_colormax(self, intmin=0, intmax=1, relativeColorbar=False):
        if self.image is not None:
            self.image.set_clim(vmin=intmin, vmax=intmax)
            self.canvas.draw_idle()

    def savePlot(self, imageData, filename, cmname=None,
                 intmin=0, intmax=1, colorbar=False):
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

    def setCaptions(self, captions):
        self.captions = captions
        self.drawCaptions(self.figure, self.ax)
        self.drawSafe()

