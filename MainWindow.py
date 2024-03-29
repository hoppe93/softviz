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

from PolarizedImage import ImageType


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
        self.separatrix = None
        self.imageMax = 0
        self.brightImageModifier = 1
        self.imageType = ImageType.I

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
        self.ui.cbColormap.addItem('RdBu')

        # Add polarized image options
        for s in ImageType:
            if s != ImageType.EMPTY:
                self.ui.cbImageType.addItem(s.value)

        #self.ui.cbImageType.addItem('Image')
        #self.ui.cbImageType.addItem('Stokes Q (+)')
        #self.ui.cbImageType.addItem('Stokes Q (-)')
        #self.ui.cbImageType.addItem('Stokes U (+)')
        #self.ui.cbImageType.addItem('Stokes U (-)')
        #self.ui.cbImageType.addItem('Stokes V (+)')
        #self.ui.cbImageType.addItem('Stokes V (-)')
        #self.ui.cbImageType.addItem('Linear polarization fraction')
        #self.ui.cbImageType.addItem('Polarization angle')
        #self.ui.cbImageType.addItem('Horizontal')
        #self.ui.cbImageType.addItem('Vertical')
        #self.ui.cbImageType.addItem('Diagonal 1')
        #self.ui.cbImageType.addItem('Diagonal 2')

        # Check command-line arguments
        if len(sys.argv) == 2:
            if os.path.isfile(sys.argv[1]):
                self.ui.txtFilename.setText(os.path.abspath(sys.argv[1]))
                self.loadFile(sys.argv[1])

        self.ui.cbColormap.setCurrentIndex(1)

    def bindEvents(self):
        self.ui.sliderIntensity.valueChanged.connect(self.intensityChanged)
        self.ui.cbPlotType.currentIndexChanged.connect(self.toggleLogarithmic)
        self.ui.cbColormap.currentIndexChanged.connect(self.setColormap)
        self.ui.cbImageType.currentIndexChanged.connect(self.setImageType)
        self.ui.cbColorbar.stateChanged.connect(self.toggleColorbar)
        self.ui.cbInvert.stateChanged.connect(self.setColormap)
        self.ui.cbBrightImage.stateChanged.connect(self.intensityChanged)
        self.ui.cbRelativeColorbar.stateChanged.connect(self.toggleColorbar)
        self.ui.cbSeparatrix.stateChanged.connect(self.showSeparatrix)
        self.ui.cbTopview.stateChanged.connect(self.showTopview)
        self.ui.cbWallCross.stateChanged.connect(self.showWallCrossSection)
        self.ui.btnOpen.clicked.connect(self.openFile)
        self.ui.btnReload.clicked.connect(self.reloadFile)
        self.ui.btnSave.clicked.connect(self.saveFile)
        self.ui.btnSetCaption.clicked.connect(self.setCaption)
        self.ui.btnWall.clicked.connect(self.setWallOverlay)

        self.captionDialog.captionsUpdated.connect(self.captionsUpdated)
        self.vesselDialog.overlayChanged.connect(self.vesselUpdated)

    def captionsUpdated(self, captions):
        self.plotWindow.image.setCaptions(captions)
        self.plotWindow.image.plotCaptions()

    def closeEvent(self, event):
        self.exit()

    def exit(self):
        self.plotWindow.close()
        self.captionDialog.close()
        self.vesselDialog.close()
        self.close()

    def intensityChanged(self):
        bim = 1
        if self.ui.cbBrightImage.isChecked():
            bim = 1.0 / 100.0

        self.ui.lblIntensity.setText(str(self.ui.sliderIntensity.value()*bim)+'%')
        intmax = (self.ui.sliderIntensity.value() / 100.0) * bim
        self.plotWindow.image.changeIntensity(intmax, relative=True)
        self.plotWindow.syntheticImageUpdated()

    def loadFile(self, filename):
        self.ui.txtFilename.setText(filename)
        self.filename = filename

        self.plotWindow.image.loadImageFile(filename, self.imageType)
        imageMax = self.plotWindow.image.getImageMax()

        # Enable overlay checkboxes
        if self.plotWindow.image.hasSeparatrix():
            self.ui.cbSeparatrix.setEnabled(True)
        if self.plotWindow.image.hasTopview():
            self.ui.cbTopview.setEnabled(True)
        if self.plotWindow.image.hasWall():
            self.ui.cbWallCross.setEnabled(True)

        if imageMax == 0:
            self.statusBar().showMessage("Image is empty!")
        else:
            #self.statusBar().showMessage("Successfully loaded "+filename, 3000)
            self.statusBar().showMessage("Max value = "+str(imageMax))

        self.refreshImage()

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(parent=self, caption="Open SOFT image file", filter="SOFT Output (*.dat *.h5 *.hdf5 *.mat *.sdt);;All files (*.*)")

        if filename:
            self.loadFile(filename)

    def refreshImage(self):
        if not self.plotWindow.isVisible():
            self.plotWindow.show()

        self.plotWindow.plotImage()

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
            self.plotWindow.image.savePlot(filename)

    def setCaption(self):
        self.captionDialog.show()

    def setColormap(self):
        cmname = self.ui.cbColormap.currentText()
        if self.ui.cbInvert.isChecked():
            self.plotWindow.image.setColormap(cmname+'_r')
            self.plotWindow.syntheticImageUpdated(True)
        else:
            self.plotWindow.image.setColormap(cmname)
            self.plotWindow.syntheticImageUpdated(True)

    def setImageType(self):
        self.imageType = ImageType(self.ui.cbImageType.currentText())
        self.reloadFile()

    def setWallOverlay(self):
        self.vesselDialog.show()

    def showSeparatrix(self):
        if self.ui.cbSeparatrix.isChecked():
            self.plotWindow.image.plotSeparatrix()
        else:
            self.plotWindow.image.removeSeparatrix()

        self.plotWindow.syntheticImageUpdated()
    
    def showTopview(self):
        if self.ui.cbTopview.isChecked():
            self.plotWindow.image.plotTopview()
        else:
            self.plotWindow.image.removeTopview()

        self.plotWindow.syntheticImageUpdated()
    
    def showWallCrossSection(self):
        if self.ui.cbWallCross.isChecked():
            self.plotWindow.image.plotWallCrossSection()
        else:
            self.plotWindow.image.removeWallCrossSection()

        self.plotWindow.syntheticImageUpdated()
    
    def toggleColorbar(self):
        self.plotWindow.image.toggleColorbar(self.ui.cbColorbar.isChecked())
        self.plotWindow.image.toggleColorbarRelative(self.ui.cbRelativeColorbar.isChecked())

        if self.ui.cbColorbar.isChecked():
            self.plotWindow.image.plotColorbar()
        else:
            self.plotWindow.image.removeColorbar()

        self.plotWindow.syntheticImageUpdated()

    def toggleLogarithmic(self):
        if self.ui.cbPlotType.currentIndex() == 1:
            self.plotWindow.image.toggleLogarithmic(True)
        else:
            self.plotWindow.image.toggleLogarithmic(False)

        self.plotWindow.syntheticImageUpdated(True)

    def vesselUpdated(self, status):
        self.plotWindow.image.setOverlays(status)
        self.plotWindow.image.plotOverlays()
        self.plotWindow.syntheticImageUpdated()

