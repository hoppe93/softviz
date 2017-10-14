# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/main.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(560, 450)
        MainWindow.setMinimumSize(QtCore.QSize(560, 450))
        MainWindow.setMaximumSize(QtCore.QSize(560, 450))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnOpen = QtWidgets.QPushButton(self.centralwidget)
        self.btnOpen.setGeometry(QtCore.QRect(420, 10, 61, 32))
        self.btnOpen.setObjectName("btnOpen")
        self.btnReload = QtWidgets.QPushButton(self.centralwidget)
        self.btnReload.setGeometry(QtCore.QRect(483, 10, 61, 32))
        self.btnReload.setObjectName("btnReload")
        self.txtFilename = QtWidgets.QLineEdit(self.centralwidget)
        self.txtFilename.setGeometry(QtCore.QRect(20, 10, 391, 32))
        self.txtFilename.setObjectName("txtFilename")
        self.cbPlotType = QtWidgets.QComboBox(self.centralwidget)
        self.cbPlotType.setGeometry(QtCore.QRect(100, 50, 441, 30))
        self.cbPlotType.setObjectName("cbPlotType")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 55, 71, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 95, 71, 20))
        self.label_2.setObjectName("label_2")
        self.cbColormap = QtWidgets.QComboBox(self.centralwidget)
        self.cbColormap.setGeometry(QtCore.QRect(100, 90, 441, 30))
        self.cbColormap.setObjectName("cbColormap")
        self.sliderIntensity = QtWidgets.QSlider(self.centralwidget)
        self.sliderIntensity.setGeometry(QtCore.QRect(10, 290, 531, 26))
        self.sliderIntensity.setMinimum(1)
        self.sliderIntensity.setMaximum(100)
        self.sliderIntensity.setPageStep(10)
        self.sliderIntensity.setProperty("value", 100)
        self.sliderIntensity.setTracking(True)
        self.sliderIntensity.setOrientation(QtCore.Qt.Horizontal)
        self.sliderIntensity.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sliderIntensity.setTickInterval(10)
        self.sliderIntensity.setObjectName("sliderIntensity")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 270, 171, 20))
        self.label_3.setObjectName("label_3")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(110, 320, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(210, 320, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(310, 320, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(420, 320, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(510, 320, 41, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(20, 320, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.btnSave = QtWidgets.QPushButton(self.centralwidget)
        self.btnSave.setGeometry(QtCore.QRect(10, 350, 94, 32))
        self.btnSave.setObjectName("btnSave")
        self.lblIntensity = QtWidgets.QLabel(self.centralwidget)
        self.lblIntensity.setGeometry(QtCore.QRect(470, 270, 63, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblIntensity.setFont(font)
        self.lblIntensity.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lblIntensity.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblIntensity.setObjectName("lblIntensity")
        self.btnInfo = QtWidgets.QPushButton(self.centralwidget)
        self.btnInfo.setGeometry(QtCore.QRect(110, 350, 94, 32))
        self.btnInfo.setObjectName("btnInfo")
        self.cbColorbar = QtWidgets.QCheckBox(self.centralwidget)
        self.cbColorbar.setGeometry(QtCore.QRect(300, 140, 181, 29))
        self.cbColorbar.setObjectName("cbColorbar")
        self.btnSetCaption = QtWidgets.QPushButton(self.centralwidget)
        self.btnSetCaption.setGeometry(QtCore.QRect(460, 350, 91, 31))
        self.btnSetCaption.setObjectName("btnSetCaption")
        self.cbInvert = QtWidgets.QCheckBox(self.centralwidget)
        self.cbInvert.setGeometry(QtCore.QRect(20, 170, 151, 26))
        self.cbInvert.setObjectName("cbInvert")
        self.cbRelativeColorbar = QtWidgets.QCheckBox(self.centralwidget)
        self.cbRelativeColorbar.setGeometry(QtCore.QRect(300, 170, 211, 26))
        self.cbRelativeColorbar.setObjectName("cbRelativeColorbar")
        self.cbBrightImage = QtWidgets.QCheckBox(self.centralwidget)
        self.cbBrightImage.setGeometry(QtCore.QRect(20, 140, 181, 26))
        self.cbBrightImage.setObjectName("cbBrightImage")
        self.cbTopview = QtWidgets.QCheckBox(self.centralwidget)
        self.cbTopview.setEnabled(False)
        self.cbTopview.setGeometry(QtCore.QRect(20, 200, 191, 26))
        self.cbTopview.setObjectName("cbTopview")
        self.btnWall = QtWidgets.QPushButton(self.centralwidget)
        self.btnWall.setGeometry(QtCore.QRect(333, 350, 121, 31))
        self.btnWall.setObjectName("btnWall")
        self.cbWallCross = QtWidgets.QCheckBox(self.centralwidget)
        self.cbWallCross.setEnabled(False)
        self.cbWallCross.setGeometry(QtCore.QRect(300, 200, 231, 26))
        self.cbWallCross.setObjectName("cbWallCross")
        self.cbSeparatrix = QtWidgets.QCheckBox(self.centralwidget)
        self.cbSeparatrix.setEnabled(False)
        self.cbSeparatrix.setGeometry(QtCore.QRect(20, 230, 241, 26))
        self.cbSeparatrix.setObjectName("cbSeparatrix")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 560, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SOFT Image Visualization"))
        self.btnOpen.setText(_translate("MainWindow", "Open..."))
        self.btnReload.setText(_translate("MainWindow", "Reload"))
        self.txtFilename.setPlaceholderText(_translate("MainWindow", "Image filename"))
        self.label.setText(_translate("MainWindow", "Plot type:"))
        self.label_2.setText(_translate("MainWindow", "Colormap:"))
        self.label_3.setText(_translate("MainWindow", "Maximum intensity level:"))
        self.label_5.setText(_translate("MainWindow", "20%"))
        self.label_6.setText(_translate("MainWindow", "40%"))
        self.label_7.setText(_translate("MainWindow", "60%"))
        self.label_8.setText(_translate("MainWindow", "80%"))
        self.label_9.setText(_translate("MainWindow", "100%"))
        self.label_10.setText(_translate("MainWindow", "0%"))
        self.btnSave.setText(_translate("MainWindow", "Save"))
        self.lblIntensity.setText(_translate("MainWindow", "100%"))
        self.btnInfo.setText(_translate("MainWindow", "Show info"))
        self.cbColorbar.setText(_translate("MainWindow", "Show colorbar"))
        self.btnSetCaption.setText(_translate("MainWindow", "Set Caption"))
        self.cbInvert.setText(_translate("MainWindow", "Invert colormap"))
        self.cbRelativeColorbar.setText(_translate("MainWindow", "Use relative color scale"))
        self.cbBrightImage.setText(_translate("MainWindow", "Bright image"))
        self.cbTopview.setText(_translate("MainWindow", "Topview"))
        self.btnWall.setText(_translate("MainWindow", "3D Wall Overlay"))
        self.cbWallCross.setText(_translate("MainWindow", "Wall cross-section"))
        self.cbSeparatrix.setText(_translate("MainWindow", "Separatrix"))

