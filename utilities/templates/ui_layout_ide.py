# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layout_ide.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(985, 565)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/control/kuttypy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("")
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.logLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logLabel.sizePolicy().hasHeightForWidth())
        self.logLabel.setSizePolicy(sizePolicy)
        self.logLabel.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(True)
        self.logLabel.setFont(font)
        self.logLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.logLabel.setObjectName("logLabel")
        self.horizontalLayout.addWidget(self.logLabel)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_6.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_6.setSpacing(2)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.filenameLabel = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filenameLabel.sizePolicy().hasHeightForWidth())
        self.filenameLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.filenameLabel.setFont(font)
        self.filenameLabel.setObjectName("filenameLabel")
        self.horizontalLayout_2.addWidget(self.filenameLabel)
        self.fontComboBox = QtWidgets.QFontComboBox(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fontComboBox.sizePolicy().hasHeightForWidth())
        self.fontComboBox.setSizePolicy(sizePolicy)
        self.fontComboBox.setObjectName("fontComboBox")
        self.horizontalLayout_2.addWidget(self.fontComboBox)
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/control/plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_3.setIcon(icon1)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy)
        self.pushButton_4.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/control/minus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_4.setIcon(icon2)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.gridLayout_6.addWidget(self.frame_2, 3, 0, 1, 1)
        self.codingTabs = QtWidgets.QTabWidget(self.frame)
        self.codingTabs.setTabsClosable(True)
        self.codingTabs.setMovable(True)
        self.codingTabs.setObjectName("codingTabs")
        self.gridLayout_6.addWidget(self.codingTabs, 2, 0, 1, 1)
        self.frame_4 = QtWidgets.QFrame(self.frame)
        self.frame_4.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_5.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_5.setSpacing(2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.fileMenuButton = QtWidgets.QPushButton(self.frame_4)
        self.fileMenuButton.setObjectName("fileMenuButton")
        self.horizontalLayout_5.addWidget(self.fileMenuButton)
        self.editMenuButton = QtWidgets.QPushButton(self.frame_4)
        self.editMenuButton.setObjectName("editMenuButton")
        self.horizontalLayout_5.addWidget(self.editMenuButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.compileButton = QtWidgets.QPushButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.compileButton.sizePolicy().hasHeightForWidth())
        self.compileButton.setSizePolicy(sizePolicy)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/control/refresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.compileButton.setIcon(icon3)
        self.compileButton.setObjectName("compileButton")
        self.horizontalLayout_5.addWidget(self.compileButton)
        self.buildOptionsButton = QtWidgets.QPushButton(self.frame_4)
        self.buildOptionsButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/control/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buildOptionsButton.setIcon(icon4)
        self.buildOptionsButton.setObjectName("buildOptionsButton")
        self.horizontalLayout_5.addWidget(self.buildOptionsButton)
        self.uploadButton = QtWidgets.QPushButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uploadButton.sizePolicy().hasHeightForWidth())
        self.uploadButton.setSizePolicy(sizePolicy)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/control/download.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.uploadButton.setIcon(icon5)
        self.uploadButton.setObjectName("uploadButton")
        self.horizontalLayout_5.addWidget(self.uploadButton)
        self.launchFirmwareButton = QtWidgets.QCheckBox(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.launchFirmwareButton.sizePolicy().hasHeightForWidth())
        self.launchFirmwareButton.setSizePolicy(sizePolicy)
        self.launchFirmwareButton.setObjectName("launchFirmwareButton")
        self.horizontalLayout_5.addWidget(self.launchFirmwareButton)
        self.gridLayout_6.addWidget(self.frame_4, 0, 0, 1, 1)
        self.reloadFrame = QtWidgets.QFrame(self.frame)
        self.reloadFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.reloadFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.reloadFrame.setObjectName("reloadFrame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.reloadFrame)
        self.horizontalLayout_3.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.reloadFrame)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.reloadLabel = QtWidgets.QLabel(self.reloadFrame)
        self.reloadLabel.setObjectName("reloadLabel")
        self.horizontalLayout_3.addWidget(self.reloadLabel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.pushButton = QtWidgets.QPushButton(self.reloadFrame)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.reloadFrame)
        self.pushButton_2.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/control/close.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon6)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        self.gridLayout_6.addWidget(self.reloadFrame, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame, 0, 0, 5, 1)
        self.termFrame = QtWidgets.QFrame(self.centralwidget)
        self.termFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.termFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.termFrame.setObjectName("termFrame")
        self.termLayout = QtWidgets.QVBoxLayout(self.termFrame)
        self.termLayout.setContentsMargins(0, 0, 0, 0)
        self.termLayout.setSpacing(0)
        self.termLayout.setObjectName("termLayout")
        self.gridLayout_2.addWidget(self.termFrame, 4, 1, 1, 1)
        self.log = QtWidgets.QTextBrowser(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.log.sizePolicy().hasHeightForWidth())
        self.log.setSizePolicy(sizePolicy)
        self.log.setMinimumSize(QtCore.QSize(400, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.log.setFont(font)
        self.log.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.log.setObjectName("log")
        self.gridLayout_2.addWidget(self.log, 3, 1, 1, 1)
        self.serialFrame = QtWidgets.QFrame(self.centralwidget)
        self.serialFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.serialFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.serialFrame.setObjectName("serialFrame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.serialFrame)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.serialData = QtWidgets.QLineEdit(self.serialFrame)
        self.serialData.setObjectName("serialData")
        self.horizontalLayout_4.addWidget(self.serialData)
        self.sendASCIIButton = QtWidgets.QPushButton(self.serialFrame)
        self.sendASCIIButton.setObjectName("sendASCIIButton")
        self.horizontalLayout_4.addWidget(self.sendASCIIButton)
        self.sendBinaryButton = QtWidgets.QPushButton(self.serialFrame)
        self.sendBinaryButton.setObjectName("sendBinaryButton")
        self.horizontalLayout_4.addWidget(self.sendBinaryButton)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.serialGuageButton = QtWidgets.QPushButton(self.serialFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serialGuageButton.sizePolicy().hasHeightForWidth())
        self.serialGuageButton.setSizePolicy(sizePolicy)
        self.serialGuageButton.setMaximumSize(QtCore.QSize(90, 16777215))
        self.serialGuageButton.setObjectName("serialGuageButton")
        self.horizontalLayout_4.addWidget(self.serialGuageButton)
        self.gridLayout_2.addWidget(self.serialFrame, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.codingTabs.setCurrentIndex(-1)
        self.serialGuageButton.clicked.connect(MainWindow.showSerialGauge) # type: ignore
        self.compileButton.clicked.connect(MainWindow.compile) # type: ignore
        self.uploadButton.clicked.connect(MainWindow.upload) # type: ignore
        self.launchFirmwareButton.clicked['bool'].connect(MainWindow.jumpToApplication) # type: ignore
        self.pushButton_4.clicked.connect(MainWindow.fontMinus) # type: ignore
        self.pushButton_3.clicked.connect(MainWindow.fontPlus) # type: ignore
        self.fontComboBox.currentTextChanged['QString'].connect(MainWindow.setFont) # type: ignore
        self.pushButton.clicked.connect(MainWindow.reloadFile) # type: ignore
        self.pushButton_2.clicked.connect(MainWindow.cancelReload) # type: ignore
        self.sendBinaryButton.clicked.connect(MainWindow.sendBinary) # type: ignore
        self.sendASCIIButton.clicked.connect(MainWindow.sendASCII) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "KuttyPy Interactive Console"))
        self.logLabel.setText(_translate("MainWindow", "Monitor registers being read and set during each operation"))
        self.filenameLabel.setText(_translate("MainWindow", ":"))
        self.fileMenuButton.setText(_translate("MainWindow", "File"))
        self.editMenuButton.setText(_translate("MainWindow", "Edit"))
        self.compileButton.setText(_translate("MainWindow", "Compile/Assemble"))
        self.uploadButton.setText(_translate("MainWindow", "Upload"))
        self.launchFirmwareButton.setText(_translate("MainWindow", "Run"))
        self.label_2.setText(_translate("MainWindow", "File Changed:"))
        self.reloadLabel.setText(_translate("MainWindow", ".."))
        self.pushButton.setText(_translate("MainWindow", "RELOAD"))
        self.sendASCIIButton.setText(_translate("MainWindow", "Send"))
        self.sendBinaryButton.setText(_translate("MainWindow", "Send Binary"))
        self.serialGuageButton.setToolTip(_translate("MainWindow", "Show serial port data in the form of a plot or dial"))
        self.serialGuageButton.setText(_translate("MainWindow", "Gauge"))
from . import resplus_rc
