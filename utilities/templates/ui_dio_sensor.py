# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dio_sensor.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(363, 300)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(3, 3, 3, 0)
        self.gridLayout.setSpacing(3)
        self.gridLayout.setObjectName("gridLayout")
        self.log_2 = QtWidgets.QCheckBox(Dialog)
        self.log_2.setObjectName("log_2")
        self.gridLayout.addWidget(self.log_2, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 1)
        self.monitors = QtWidgets.QStackedWidget(Dialog)
        self.monitors.setObjectName("monitors")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.gaugeLayout = QtWidgets.QHBoxLayout(self.page)
        self.gaugeLayout.setContentsMargins(5, 5, 5, 5)
        self.gaugeLayout.setObjectName("gaugeLayout")
        self.monitors.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.page_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.graph = PlotWidget(self.page_2)
        self.graph.setObjectName("graph")
        self.horizontalLayout_2.addWidget(self.graph)
        self.monitors.addWidget(self.page_2)
        self.gridLayout.addWidget(self.monitors, 2, 0, 1, 5)
        self.switcher = QtWidgets.QPushButton(Dialog)
        self.switcher.setObjectName("switcher")
        self.gridLayout.addWidget(self.switcher, 0, 3, 1, 1)
        self.configLayout = QtWidgets.QHBoxLayout()
        self.configLayout.setObjectName("configLayout")
        self.gridLayout.addLayout(self.configLayout, 1, 0, 1, 4)

        self.retranslateUi(Dialog)
        self.monitors.setCurrentIndex(0)
        self.log_2.toggled['bool'].connect(Dialog.changeRange)
        self.pushButton.clicked.connect(Dialog.initialize)
        self.switcher.clicked.connect(Dialog.next)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "ADC Configuration"))
        self.log_2.setText(_translate("Dialog", "Scale"))
        self.pushButton.setText(_translate("Dialog", "Initialize"))
        self.switcher.setText(_translate("Dialog", "Data Logger"))

from pyqtgraph import PlotWidget
