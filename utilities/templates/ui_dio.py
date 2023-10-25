# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dio.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_stack(object):
    def setupUi(self, stack):
        stack.setObjectName("stack")
        stack.resize(270, 27)
        self.inputPage = QtWidgets.QWidget()
        self.inputPage.setObjectName("inputPage")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.inputPage)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.nameIn = QtWidgets.QCheckBox(self.inputPage)
        self.nameIn.setObjectName("nameIn")
        self.horizontalLayout.addWidget(self.nameIn)
        self.pullup = QtWidgets.QCheckBox(self.inputPage)
        self.pullup.setObjectName("pullup")
        self.horizontalLayout.addWidget(self.pullup)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.inputPage)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        stack.addWidget(self.inputPage)
        self.outputPage = QtWidgets.QWidget()
        self.outputPage.setObjectName("outputPage")
        self.outputLayout = QtWidgets.QHBoxLayout(self.outputPage)
        self.outputLayout.setContentsMargins(0, 0, 0, 0)
        self.outputLayout.setSpacing(0)
        self.outputLayout.setObjectName("outputLayout")
        self.nameOut = QtWidgets.QCheckBox(self.outputPage)
        self.nameOut.setCheckable(True)
        self.nameOut.setChecked(False)
        self.nameOut.setTristate(False)
        self.nameOut.setObjectName("nameOut")
        self.outputLayout.addWidget(self.nameOut)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.outputLayout.addItem(spacerItem1)
        self.pushButton_2 = QtWidgets.QPushButton(self.outputPage)
        self.pushButton_2.setObjectName("pushButton_2")
        self.outputLayout.addWidget(self.pushButton_2)
        stack.addWidget(self.outputPage)

        self.retranslateUi(stack)
        stack.setCurrentIndex(0)
        self.nameOut.clicked['bool'].connect(stack.setOutputState) # type: ignore
        self.pullup.clicked['bool'].connect(stack.setOutputState) # type: ignore
        self.pushButton.clicked.connect(stack.next) # type: ignore
        self.pushButton_2.clicked.connect(stack.next) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(stack)

    def retranslateUi(self, stack):
        _translate = QtCore.QCoreApplication.translate
        stack.setWindowTitle(_translate("stack", "StackedWidget"))
        self.nameIn.setText(_translate("stack", "name"))
        self.pullup.setText(_translate("stack", "Pull-Up"))
        self.pullup.setProperty("class", _translate("stack", "pullup"))
        self.pushButton.setText(_translate("stack", "INPUT"))
        self.nameOut.setText(_translate("stack", "name"))
        self.pushButton_2.setText(_translate("stack", "OUTPUT"))
