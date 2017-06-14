# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/setcaption.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SetCaption(object):
    def setupUi(self, SetCaption):
        SetCaption.setObjectName("SetCaption")
        SetCaption.resize(875, 309)
        self.buttonBox = QtWidgets.QDialogButtonBox(SetCaption)
        self.buttonBox.setGeometry(QtCore.QRect(780, 10, 81, 461))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.btnAddCaption = QtWidgets.QPushButton(SetCaption)
        self.btnAddCaption.setGeometry(QtCore.QRect(10, 270, 84, 28))
        self.btnAddCaption.setObjectName("btnAddCaption")
        self.tblCaptions = QtWidgets.QTableWidget(SetCaption)
        self.tblCaptions.setGeometry(QtCore.QRect(10, 10, 761, 251))
        self.tblCaptions.setRowCount(1)
        self.tblCaptions.setColumnCount(4)
        self.tblCaptions.setObjectName("tblCaptions")

        self.retranslateUi(SetCaption)
        self.buttonBox.accepted.connect(SetCaption.accept)
        self.buttonBox.rejected.connect(SetCaption.reject)
        QtCore.QMetaObject.connectSlotsByName(SetCaption)

    def retranslateUi(self, SetCaption):
        _translate = QtCore.QCoreApplication.translate
        SetCaption.setWindowTitle(_translate("SetCaption", "Set Caption"))
        self.btnAddCaption.setText(_translate("SetCaption", "Add"))

