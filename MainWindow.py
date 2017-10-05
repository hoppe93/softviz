from PyQt5 import QtWidgets
from ui import main_design
from PlotWindow import PlotWindow
from SetCaption import SetCaption
from Vessel import Vessel
import sys
import os.path
import numpy as np
import scipy.io
import h5py
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = main_design.Ui_MainWindow()
        self.ui.setupUi(self)

        self.image = None
        self.filename = ""
        self.detectorPosition = None
        self.detectorDirection = None
        self.detectorVisang = None
        self.wall = None
        self.imageMax = 0
        self.brightImageModifier = 1

        # Create plot window
        self.plotWindow = PlotWindow()
        # Create caption dialog
        self.captionDialog = SetCaption()
        # Create vessel dialog
        self.vesselDialog = Vessel()

        # Bind to events
        self.bindEvents()

        # Add plot types
        self.ui.cbPlotType.addItem('Normal', 0)
        self.ui.cbPlotType.addItem('Logarithmic', 1)

        # Add color map options
        self.ui.cbColormap.addItem('afmhot')
        self.ui.cbColormap.addItem('GeriMap')
        self.ui.cbColormap.addItem('gray')
        self.ui.cbColormap.addItem('viridis')
        self.ui.cbColormap.addItem('jet')

        # Check command-line arguments
        if len(sys.argv) == 2:
            if os.path.isfile(sys.argv[1]):
                self.ui.txtFilename.setText(os.path.abspath(sys.argv[1]))
                self.loadFile(sys.argv[1])

        # Register GeriMap
        gm = [(0, 0, 0), (.15, .15, .5), (.3, .15, .75),
              (.6, .2, .50), (1, .25, .15), (.9, .5, 0),
              (.9, .75, .1), (.9, .9, .5), (1, 1, 1)]
        gerimap = LinearSegmentedColormap.from_list('GeriMap', gm)
        gerimap_r = LinearSegmentedColormap.from_list('GeriMap_r', gm[::-1])
        plt.register_cmap(cmap=gerimap)
        plt.register_cmap(cmap=gerimap_r)

        self.ui.cbColormap.setCurrentIndex(1)

    def bindEvents(self):
        self.ui.sliderIntensity.valueChanged.connect(self.intensityChanged)
        self.ui.cbPlotType.currentIndexChanged.connect(self.refreshImage)
        self.ui.cbColormap.currentIndexChanged.connect(self.refreshImage)
        self.ui.cbColorbar.stateChanged.connect(self.refreshImage)
        self.ui.cbInvert.stateChanged.connect(self.refreshImage)
        self.ui.cbBrightImage.stateChanged.connect(self.intensityChanged)
        self.ui.cbRelativeColorbar.stateChanged.connect(self.refreshImage)
        self.ui.cbTopview.stateChanged.connect(self.showTopview)
        self.ui.btnOpen.clicked.connect(self.openFile)
        self.ui.btnReload.clicked.connect(self.reloadFile)
        self.ui.btnSave.clicked.connect(self.saveFile)
        self.ui.btnSetCaption.clicked.connect(self.setCaption)
        self.ui.btnWall.clicked.connect(self.setWallOverlay)

        self.captionDialog.captionsUpdated.connect(self.captionsUpdated)
        self.vesselDialog.overlayChanged.connect(self.vesselUpdated)

    def captionsUpdated(self, captions):
        self.plotWindow.setCaptions(captions)

    def closeEvent(self, event):
        self.exit()

    def exit(self):
        self.plotWindow.close()
        self.captionDialog.close()
        self.vesselDialog.close()
        self.close()

    def getImage(self):
        img = self.image
        imgmax = self.imageMax
        zerolevel = 0

        if self.ui.cbPlotType.currentIndex() == 1:  # Normal
            img = np.log10(img)
            imgmax = np.log10(imgmax)
            zerolevel = imgmax - 40

            for i in range(0, len(img)-1):
                for j in range(0, len(img[i])-1):
                    if np.isinf(img[i][j]) or np.isnan(img[i][j]):
                        img[i][j] = zerolevel

        return img, imgmax, zerolevel

    def intensityChanged(self):
        bim = 1
        if self.ui.cbBrightImage.isChecked():
            bim = 1.0 / 100.0

        self.ui.lblIntensity.setText(str(self.ui.sliderIntensity.value()*bim)+'%')

        imgmax = self.imageMax
        zerolevel = 0
        if self.ui.cbPlotType.currentIndex() == 1:
            imgmax = np.log10(imgmax)
            zerolevel = imgmax - 40

        intmax = imgmax * (self.ui.sliderIntensity.value() / 100.0) * bim
        self.plotWindow.set_colormax(zerolevel, intmax, relativeColorbar=self.ui.cbRelativeColorbar.isChecked())

    def loadFile(self, filename):
        self.ui.txtFilename.setText(filename)
        self.filename = filename
        self.readfile(filename)
        self.imageMax = np.amax(self.image)

        if np.amax(np.amax(np.abs(self.image))) == 0:
            self.statusBar().showMessage("Image is empty!")
        else:
            #self.statusBar().showMessage("Successfully loaded "+filename, 3000)
            self.statusBar().showMessage("Max value = "+str(self.imageMax))

        self.refreshImage()

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(parent=self, caption="Open SOFT image file", filter="SOFT Output (*.dat *.h5 *.hdf5 *.mat *.sdt);;All files (*.*)")

        if filename:
            self.loadFile(filename)

    def readfile(self, filename):
        # DAT-file: for legacy support
        if filename.endswith('.dat') or filename.endswith('.topview'):
            self.image = np.genfromtxt(filename)
            self.ui.cbTopview.setEnabled(False)
        elif filename.endswith('.mat'):
            try:
                matfile = scipy.io.loadmat(filename)

                self.image = np.transpose(matfile['image'])
                #self.image = matfile['image']
                self.detectorPosition = matfile['detectorPosition'][0]
                self.detectorDirection = matfile['detectorDirection'][0]
                self.detectorVisang = matfile['detectorVisang'][0]
                self.wall = matfile['wall']
            except NotImplementedError:
                matfile = h5py.File(filename)

                self.image = np.transpose(matfile['image'][:,:])
                self.detectorPosition = matfile['detectorPosition'][:,0]
                self.detectorDirection = matfile['detectorDirection'][:,0]
                #self.detectorPosition = np.array([0,-3,0])
                #self.detectorDirection = np.array([0,1,0])
                self.detectorVisang = matfile['detectorVisang'][0,0]
                self.wall = matfile['wall'][:,:]

            self.wall_rmax = np.amax(self.wall[0,:])
            self.wall_rmin = np.amin(self.wall[0,:])
            self.plotWindow.setWall(self.wall)
            self.plotWindow.setCamera(self.detectorPosition, self.detectorDirection, self.detectorVisang)
        else:
            print('ERROR: Unrecognized image format. Unable to load file.')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(e.strerror)
            msg.setWindowTitle('Error loading file')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def refreshImage(self):
        img, imgmax, zerolevel = self.getImage()
        if img is None:
            return

        bim = 1
        if self.ui.cbBrightImage.isChecked():
            bim = 1.0 / 100.0

        intmax = imgmax * (self.ui.sliderIntensity.value() / 100.0) * bim

        # Select colormap
        cmname = self.ui.cbColormap.currentText()
        # Show colorbar?
        cbar = self.ui.cbColorbar.isChecked()

        # Invert colormap?
        if self.ui.cbInvert.isChecked():
            cmname = cmname + '_r'

        if not self.plotWindow.isVisible():
            self.plotWindow.show()

        self.plotWindow.plotImage(img, cmname=cmname,
                                  intmin=zerolevel, intmax=intmax,
                                  colorbar=cbar,
                                  relativeColorbar=self.ui.cbRelativeColorbar.isChecked())

    def reloadFile(self):
        if self.filename is "":
            return

        self.loadFile(self.filename)

    def saveFile(self):
        if not self.plotWindow.isVisible():
            QMessageBox.information(self, 'No image open', 'No SOFT image file is currently open, thus there is no image to save. Please, open an image file!')
            return

        filename, _ = QFileDialog.getSaveFileName(self, caption='Save SOFT image', filter='Encapsulated Post-Script (*.eps);;Portable Network Graphics (*.png);;Portable Document Format (*.pdf);;Scalable Vector Graphics (*.svg)')

        if filename:
            img, imgmax, zerolevel = self.getImage()
            intmax = imgmax * (self.ui.sliderIntensity.value() / 100.0)
            cmname = self.ui.cbColormap.currentText()
            cbar = self.ui.cbColorbar.isChecked()

            if self.ui.cbBrightImage.isChecked():
                intmax = intmax / 100.0

            # Invert colormap?
            if self.ui.cbInvert.isChecked():
                cmname = cmname + '_r'

            self.plotWindow.savePlot(img, filename, cmname=cmname, intmin=zerolevel,
                                     intmax=intmax, colorbar=cbar)

    def setCaption(self):
        self.captionDialog.show()

    def setWallOverlay(self):
        self.vesselDialog.show()

    def showTopview(self):
        if self.wall == None: return
        self.plotWindow.setTopview(rmin=self.wall_rmin, rmax=self.wall_rmax, show=self.ui.cbTopview.isChecked())

    def vesselUpdated(self, status):
        self.plotWindow.setVesselPlot(status)

