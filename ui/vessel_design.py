# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/vessel.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Vessel(object):
    def setupUi(self, Vessel):
        Vessel.setObjectName("Vessel")
        Vessel.resize(540, 450)
        self.buttonBox = QtWidgets.QDialogButtonBox(Vessel)
        self.buttonBox.setGeometry(QtCore.QRect(190, 410, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gbCrossSection = QtWidgets.QGroupBox(Vessel)
        self.gbCrossSection.setGeometry(QtCore.QRect(10, 50, 521, 81))
        self.gbCrossSection.setFlat(False)
        self.gbCrossSection.setCheckable(True)
        self.gbCrossSection.setObjectName("gbCrossSection")
        self.cbCSWall = QtWidgets.QCheckBox(self.gbCrossSection)
        self.cbCSWall.setGeometry(QtCore.QRect(10, 30, 231, 26))
        self.cbCSWall.setChecked(True)
        self.cbCSWall.setObjectName("cbCSWall")
        self.cbCSSeparatrix = QtWidgets.QCheckBox(self.gbCrossSection)
        self.cbCSSeparatrix.setGeometry(QtCore.QRect(260, 30, 251, 26))
        self.cbCSSeparatrix.setObjectName("cbCSSeparatrix")
        self.cbCSFlux = QtWidgets.QCheckBox(self.gbCrossSection)
        self.cbCSFlux.setGeometry(QtCore.QRect(10, 50, 221, 26))
        self.cbCSFlux.setObjectName("cbCSFlux")
        self.tbEqData = QtWidgets.QLineEdit(Vessel)
        self.tbEqData.setGeometry(QtCore.QRect(10, 10, 441, 28))
        self.tbEqData.setText("")
        self.tbEqData.setObjectName("tbEqData")
        self.pushButton = QtWidgets.QPushButton(Vessel)
        self.pushButton.setGeometry(QtCore.QRect(443, 10, 91, 28))
        self.pushButton.setObjectName("pushButton")
        self.groupBox = QtWidgets.QGroupBox(Vessel)
        self.groupBox.setEnabled(False)
        self.groupBox.setGeometry(QtCore.QRect(10, 140, 521, 261))
        self.groupBox.setCheckable(True)
        self.groupBox.setChecked(True)
        self.groupBox.setObjectName("groupBox")

        self.retranslateUi(Vessel)
        self.buttonBox.accepted.connect(Vessel.accept)
        self.buttonBox.rejected.connect(Vessel.reject)
        QtCore.QMetaObject.connectSlotsByName(Vessel)

    def retranslateUi(self, Vessel):
        _translate = QtCore.QCoreApplication.translate
        Vessel.setWindowTitle(_translate("Vessel", "Vessel Contours"))
        self.gbCrossSection.setTitle(_translate("Vessel", "Cross-section in tangential plane"))
        self.cbCSWall.setText(_translate("Vessel", "Wall"))
        self.cbCSSeparatrix.setText(_translate("Vessel", "Separatrix"))
        self.cbCSFlux.setText(_translate("Vessel", "Flux contours"))
        self.tbEqData.setPlaceholderText(_translate("Vessel", "Equilibrium Data"))
        self.pushButton.setText(_translate("Vessel", "Browse..."))
        self.groupBox.setTitle(_translate("Vessel", "3D Overlay"))

