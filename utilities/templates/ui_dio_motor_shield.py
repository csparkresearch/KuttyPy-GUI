# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dio_motor_shield.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(627, 326)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setAutoRepeat(True)
        self.pushButton_4.setAutoRepeatInterval(20)
        self.pushButton_4.setAutoDefault(False)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 2, 2, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setAutoRepeat(True)
        self.pushButton_3.setAutoRepeatInterval(20)
        self.pushButton_3.setAutoDefault(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 0, 2, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setAutoRepeat(True)
        self.pushButton_5.setAutoRepeatInterval(20)
        self.pushButton_5.setAutoDefault(False)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 1, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setAutoRepeat(True)
        self.pushButton_2.setAutoRepeatInterval(20)
        self.pushButton_2.setAutoDefault(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.pushButton_6 = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setAutoRepeat(True)
        self.pushButton_6.setAutoRepeatInterval(20)
        self.pushButton_6.setAutoDefault(False)
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout.addWidget(self.pushButton_6, 1, 2, 1, 1)

        self.retranslateUi(Dialog)
        self.pushButton_2.clicked.connect(Dialog.stepLeft) # type: ignore
        self.pushButton_5.clicked.connect(Dialog.stepRight) # type: ignore
        self.pushButton_3.clicked.connect(Dialog.stepForward) # type: ignore
        self.pushButton_4.clicked.connect(Dialog.stepBackward) # type: ignore
        self.pushButton_6.clicked.connect(Dialog.stop) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton_4.setText(_translate("Dialog", "BACKWARD"))
        self.pushButton_3.setText(_translate("Dialog", "FORWARD"))
        self.pushButton_5.setText(_translate("Dialog", ">"))
        self.pushButton_2.setText(_translate("Dialog", "<"))
        self.pushButton_6.setText(_translate("Dialog", "STOP"))
from . import res_rc
