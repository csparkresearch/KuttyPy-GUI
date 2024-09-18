'''
'''
# !/usr/bin/python3

import os, sys, time, re, traceback, platform
from PyQt5 import QtGui, QtCore, QtWidgets
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import KuttyPyLib
import socket

from utilities.templates import ui_layout_ide as layout
from utilities import uploader, syntax, REGISTERS, dio
from utilities import texteditor
import constants
import inspect

from functools import partial
from collections import OrderedDict


# translation stuff
def translate(lang=None):
    global app, t, t1
    if lang is None:
        lang = QtCore.QLocale.system().name()
    t = QtCore.QTranslator()
    t.load("lang/" + lang, os.path.dirname(__file__))
    app.installTranslator(t)
    t1 = QtCore.QTranslator()
    t1.load("qt_" + lang,
            QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(t1)


class myTimer():
    def __init__(self, interval):
        self.interval = interval
        self.reset()

    def reset(self):
        self.timeout = time.time() + self.interval

    def ready(self):
        T = time.time()
        dt = T - self.timeout
        if dt > 0:  # timeout is ahead of current time
            # if self.interval>5:print('reset',self.timeout,dt)
            self.timeout = T - dt % self.interval + self.interval
            # if self.interval>5:print(self.timeout)
            return True
        return False

    def progress(self):
        return 100 * (self.interval - self.timeout + time.time()) / (self.interval)


LKP = True


class AppWindow(QtWidgets.QMainWindow, layout.Ui_MainWindow):
    p = None
    logThis = QtCore.pyqtSignal(str)
    showStatusSignal = QtCore.pyqtSignal(str, bool)
    serverSignal = QtCore.pyqtSignal(str)
    logThisPlain = QtCore.pyqtSignal(bytes)
    codeOutput = QtCore.pyqtSignal(str, str)
    serialGaugeSignal = QtCore.pyqtSignal(bytes)
    serialGaugeConvert = 'bytes'
    serialStream = b''

    def __init__(self, parent=None, **kwargs):
        super(AppWindow, self).__init__(parent)

        self.local_ip = 'localhost'
        self.setupUi(self)

        self.fs_watcher = None
        self.reloadFrame.setVisible(False)

        self.compile_thread = None

        self.monitoring = True
        self.userHexRunning = False
        self.uploadingHex = False
        self.autoUpdateUserRegisters = False
        self.CFile = None  # '~/kuttyPy.c'
        self.defaultDirectory = path["examples"]
        self.serverActive = False
        self.VERSION = REGISTERS.VERSION_ATMEGA32  # This needs to be dynamically changed when hardware is connected

        self.serialFrame.hide()  # Hide the serial guage button
        # Define some keyboard shortcuts for ease of use
        self.shortcutActions = {}
        self.shortcuts = {"f": partial(self.setLanguage, 'fr_FR'), "e": partial(self.setLanguage, 'en_IN'),
                          "m": partial(self.setLanguage, 'ml_IN')}
        for a in self.shortcuts:
            shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(a), self)
            shortcut.activated.connect(self.shortcuts[a])
            self.shortcutActions[a] = shortcut

        ########## C CODE EDITOR SYNTAX HIGHLIGHTER
        self.code_highlighters = []
        ####### C CODE EDITOR #########
        self.codingTabs.tabCloseRequested.connect(self.closeCTab)
        self.codingTabs.tabBarClicked.connect(self.CTabChanged)
        self.listTab = None
        self.mapTab = None
        self.hexTab = None
        self.serialGaugeSignal.connect(self.setSerialgauge)
        self.logThisPlain.connect(self.appendLogPlain)  # Connect to the log window

        self.activeEditor = None
        self.activeSourceTab = None
        self.sourceTabs = {}
        self.addSourceTab()

        ######### C CODE UPLOADER
        self.uploadThread = QtCore.QThread()
        self.UploadObject = self.uploadObject()
        self.UploadObject.moveToThread(self.uploadThread)
        self.UploadObject.finished.connect(self.uploadThread.quit)
        self.UploadObject.logThis.connect(self.appendLog)  # Connect to the log window
        self.UploadObject.resultSignal.connect(self.codeOutput)  # Load .lst, .hex , .map files
        self.UploadObject.logThisPlain.connect(self.appendLogPlain)  # Connect to the log window. add plain text
        self.logThis.connect(self.appendLog)  # Connect to the log window

        self.uploadThread.started.connect(self.UploadObject.execute)
        self.uploadThread.finished.connect(self.codeFinished)

        self.statusBar = self.statusBar()
        self.makeBottomMenu()
        self.addFileMenu()
        self.addEditMenu()
        self.addBuildOptionsMenu()

        self.editorFont = QtGui.QFont()
        self.editorFont.setPointSize(12)
        self.editorFont.setFamily('Ubuntu mono')

        global app

        self.initializeCommunications()
        self.pending = {
            'status': myTimer(constants.STATUS_UPDATE_INTERVAL),
            'update': myTimer(constants.AUTOUPDATE_INTERVAL),
        }

        serialgaugeoptions = {'name': 'Serial Monitor', 'init': print, 'read': None,
                              'fields': ['Value'],
                              'min': [0],
                              'max': [1000],
                              'config': [{
                                  'name': 'Data Type',
                                  'options': ['byte', 'ASCII'],
                                  'function': self.configSerialGauge
                              }
                              ]}
        self.serialGauge = dio.DIOSENSOR(self, serialgaugeoptions)

        self.startTime = time.time()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateEverything)
        self.timer.start(20)

        # Auto-Detector
        self.shortlist = KuttyPyLib.getFreePorts()

    def closeEvent(self, event):
        self.external.terminate()
        self.external.waitForFinished(1000)

    def embedTerminal(self):
        import subprocess
        system = platform.system()
        self.external = QtCore.QProcess(self)
        if system == 'Linux':
            self.external.start('gnome-terminal', ["--working-directory", self.defaultDirectory])
        if system == 'Windows':
            self.external.start('cmd')

        '''
		time.sleep(1)
		self.external.write(b"hello")

		p = subprocess.run(['xprop', '-root'], stdout=subprocess.PIPE)
		for line in p.stdout.decode().splitlines():
			m = re.fullmatch(r'^_NET_ACTIVE_WINDOW.*[)].*window id # (0x[0-9a-f]+)', line)
			if m:
				window = QtGui.QWindow.fromWinId(int(m.group(1), 16))
				window.setFlag(QtCore.Qt.FramelessWindowHint, True)
				widget = QtWidgets.QWidget.createWindowContainer(
					window, self.termFrame, QtCore.Qt.FramelessWindowHint)
				widget.setFixedSize(600, 400)
				self.termLayout.addWidget(widget)
				# this is where the magic happens...
				self.external.finished.connect(self.close_maybe)
				break
		else:
			QtWidgets.QMessageBox.warning(self, 'Error', 'Could not find WID for curreent Window')
		'''

    def close_maybe(self):
        print('terminal closed')
        pass

    def activateCompileServer(self):
        if self.serverActive:  # Stop it
            '''
			if self.compile_thread is not None:
				self.compile_thread.terminate()
				self.compile_thread.wait()
				print('quit compile_thread')
				self.compile_thread_button.setParent(None)
				self.showStatus("Compiler Stopped ", False)
				return
			self.serverActive = False
			self.compile_thread_button.setText("Online Compiler")
			'''
            return
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)  # Set a timeout to avoid blocking indefinitely
            try:
                s.connect(("8.8.8.8", 80))  # Connect to a public IP address
                self.local_ip = s.getsockname()[0]
            except:
                self.local_ip = 'localhost'

            from online.compile_server import create_server
            self.compile_thread = create_server(self.showStatusSignal, self.serverSignal, path, self.local_ip, self.p)
            self.showStatusSignal.connect(self.showStatus)
            self.serverSignal.connect(self.showServerStatus)
            s.close()
            self.showStatus("Visual Coding and Compiler Active at " + self.local_ip+":5000", False)
            self.compile_thread_button.setText(self.local_ip)
            self.serverActive = True

    def addFileMenu(self):
        codeMenu = QtWidgets.QMenu()

        newFileAction = QtWidgets.QAction('New File', self)
        newFileAction.setShortcut(QtGui.QKeySequence("Ctrl+N"))
        ico = QtGui.QIcon()
        ico.addPixmap(QtGui.QPixmap(":/control/plus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        newFileAction.setIcon(ico)
        newFileAction.triggered.connect(self.addSourceTab)
        codeMenu.addAction(newFileAction)

        openFileAction = QtWidgets.QAction('Open File', self)
        openFileAction.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        openFileAction.triggered.connect(self.openFile)
        openIcon = QtGui.QIcon()
        openIcon.addPixmap(QtGui.QPixmap(":/control/document-open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        openFileAction.setIcon(openIcon)
        codeMenu.addAction(openFileAction)

        saveFileAction = QtWidgets.QAction('Save File', self)
        saveFileAction.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        saveFileAction.triggered.connect(self.saveFile)
        saveIcon = QtGui.QIcon()
        saveIcon.addPixmap(QtGui.QPixmap(":/control/saveall.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        saveFileAction.setIcon(saveIcon)
        codeMenu.addAction(saveFileAction)

        saveAsFileAction = QtWidgets.QAction('Save As', self)
        saveAsFileAction.setShortcut(QtGui.QKeySequence("Ctrl+Shift+S"))
        saveAsFileAction.triggered.connect(self.saveAs)
        saveAsFileAction.setIcon(saveIcon)
        codeMenu.addAction(saveAsFileAction)

        a = QtWidgets.QAction('Terminal', self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+Shift+T"))
        a.triggered.connect(self.embedTerminal)
        termIcon = QtGui.QIcon()
        termIcon.addPixmap(QtGui.QPixmap(":/control/utilities-terminal.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        a.setIcon(termIcon)
        codeMenu.addAction(a)

        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        codeMenu.addAction(exitAction)
        self.fileMenuButton.setMenu(codeMenu)

    def addBuildOptionsMenu(self):
        codeMenu = QtWidgets.QMenu()
        toggleLKPAction = QtWidgets.QAction('Include KP Library', self)
        toggleLKPAction.setCheckable(True)
        toggleLKPAction.setChecked(True)
        toggleLKPAction.triggered[bool].connect(self.setLKP)
        codeMenu.addAction(toggleLKPAction)
        self.buildOptionsButton.setMenu(codeMenu)

    def setLKP(self, state):
        global LKP
        print('LKP linking', state)
        LKP = state

    def closeEvent(self, evnt):
        evnt.ignore()
        self.askBeforeQuit()

    def askBeforeQuit(self):
        ask = False
        for editors in self.sourceTabs:
            if self.sourceTabs[editors][0].changed:
                ask = True
        if ask:
            reply = QtWidgets.QMessageBox.question(self, 'Warning', 'Files may have unsaved changes.\nReally quit?',
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return

        self.userHexRunning = False
        global app
        app.quit()

    def addEditMenu(self):
        codeMenu = QtWidgets.QMenu()

        undoAction = QtWidgets.QAction('Undo', self)
        undoAction.setShortcut(QtGui.QKeySequence("Ctrl+Z"))
        undoAction.triggered.connect(self.activeEditor.undo)
        ico = QtGui.QIcon()
        ico.addPixmap(QtGui.QPixmap(":/control/reset.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        undoAction.setIcon(ico)
        codeMenu.addAction(undoAction)

        redoAction = QtWidgets.QAction('Redo', self)
        redoAction.setShortcut(QtGui.QKeySequence("Ctrl+Shift+Z"))
        redoAction.triggered.connect(self.activeEditor.redo)
        codeMenu.addAction(redoAction)
        a = QtWidgets.QAction('Cut', self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+X"))
        a.triggered.connect(self.activeEditor.cut)
        codeMenu.addAction(a)
        a = QtWidgets.QAction('Copy', self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+C"))
        a.triggered.connect(self.activeEditor.copy)
        codeMenu.addAction(a)
        a = QtWidgets.QAction('Paste', self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+V"))
        a.triggered.connect(self.activeEditor.paste)
        codeMenu.addAction(a)
        a = QtWidgets.QAction('Select All', self)
        a.setShortcut(QtGui.QKeySequence("Ctrl+A"))
        a.triggered.connect(self.activeEditor.selectAll)
        codeMenu.addAction(a)

        self.editMenuButton.setMenu(codeMenu)

    def makeBottomMenu(self):
        try:
            self.pushbutton.setParent(None)
        except:
            pass
        self.pushbutton = QtWidgets.QPushButton('Menu')
        self.pushbutton.setStyleSheet("color: #262;")
        menu = QtWidgets.QMenu()

        menu.addAction('Save Window as Svg', self.exportSvg)
        menu.addAction('Upload Hex File', self.uploadHex)

        # Theme
        self.themeAction = QtWidgets.QWidgetAction(menu)
        themes = [a.split('.qss')[0] for a in os.listdir(path["themes"]) if '.qss' in a]
        self.themeBox = QtWidgets.QComboBox();
        self.themeBox.addItems(themes)
        self.themeBox.currentIndexChanged['QString'].connect(self.setTheme)
        self.themeAction.setDefaultWidget(self.themeBox)
        menu.addAction(self.themeAction)

        defaultTheme = "newtheme"
        self.themeBox.setCurrentIndex(themes.index(defaultTheme))
        self.setTheme(defaultTheme)

        self.pushbutton.setMenu(menu)

        # Compile thread
        self.compile_thread_button = QtWidgets.QPushButton('Visual Coding/Online Compiler')
        self.compile_thread_button.setStyleSheet("color: #262;")
        self.compile_thread_button.clicked.connect(self.activateCompileServer)
        self.statusBar.addPermanentWidget(self.compile_thread_button)

        self.bottomLabel = QtWidgets.QLabel("Messages")

        # Menu button
        self.statusBar.addPermanentWidget(self.pushbutton)

    def closeCTab(self, index):
        print('Close Tab', index)
        widget = self.codingTabs.widget(index)
        sourceTabClosed = False
        if widget == self.mapTab:
            print('closing map tab')
            self.mapTab = None
        elif widget == self.hexTab:
            print('closing hex tab')
            self.hexTab = None
        elif widget == self.listTab:
            print('closing list tab')
            self.listTab = None
        elif widget in self.sourceTabs:
            if len(self.sourceTabs) == 1:
                print("last tab. won't close.")
                return
            else:
                print('closing source tab', widget.objectName())
                self.closeCompileTabs(self.codingTabs.tabText(self.codingTabs.indexOf(widget)))
                self.sourceTabs.pop(widget)
                sourceTabClosed = True

        self.codingTabs.removeTab(index)
        if sourceTabClosed:  # Source Tab closed. Re-assign active source tab
            self.activeSourceTab = list(self.sourceTabs.keys())[0]
            self.activeEditor = self.sourceTabs[self.activeSourceTab][0]
            self.CFile = self.sourceTabs[self.activeSourceTab][1]
            self.codingTabs.setCurrentIndex(self.codingTabs.indexOf(self.activeSourceTab))
            print('New Source Tab:', self.getActiveFilename(), self.CFile)

    def closeCompileTabs(self, fullname):
        name = os.path.split(fullname)[1].split('.')[0]
        for tab, ext in zip([self.mapTab, self.hexTab, self.listTab], ['.map', '.hex', '.lst']):
            if tab is not None:
                print(self.codingTabs.tabText(self.codingTabs.indexOf(tab)), name + ext)
                if self.codingTabs.tabText(self.codingTabs.indexOf(tab)) == name + ext:
                    self.codingTabs.removeTab(self.codingTabs.indexOf(tab))
        # print(f"closing {ext} tab")

        pass

    def getActiveFilename(self):
        self.codingTabs.tabText(self.codingTabs.indexOf(self.activeSourceTab))

    def addSourceTab(self):
        sourceTab = QtWidgets.QWidget()
        sourceTab.setObjectName("sourceTab")
        horizontalLayout_3 = QtWidgets.QHBoxLayout(sourceTab)
        horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        horizontalLayout_3.setSpacing(0)
        horizontalLayout_3.setObjectName("horizontalLayout_3")
        editor = texteditor.myTextEditor(sourceTab, self.codingTabs)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        font.setPointSize(12)
        editor.setFont(font)
        editor.setObjectName("editor")
        editor.setTabChangesFocus(False)
        horizontalLayout_3.addWidget(editor)
        self.codingTabs.addTab(sourceTab, "")
        self.sourceTabs[sourceTab] = [editor, None]
        self.codingTabs.setCurrentIndex(self.codingTabs.indexOf(sourceTab))
        self.codingTabs.setTabText(self.codingTabs.indexOf(sourceTab), 'Untitled')
        self.CFile = None
        self.activeSourceTab = sourceTab
        self.activeEditor = editor
        self.code_highlighters.append(syntax.CHighlighter(editor.document()))

    def CTabChanged(self, index):
        widget = self.codingTabs.widget(index)
        if widget in self.sourceTabs:
            self.activeSourceTab = widget
            self.activeEditor = self.sourceTabs[widget][0]
            self.CFile = self.sourceTabs[widget][1]
            self.filenameLabel.setText(self.CFile)
            print('Change Tab', index, self.codingTabs.tabText(index), self.CFile)

    def newRegister(self):
        reg = dio.REGEDIT(self.commandQ)
        # self.registerLayout.addWidget(reg)
        # self.registers.append(reg)

        # TODO: Convert layout to listwidget to enable re-ordering
        regItem = QtWidgets.QListWidgetItem()
        regItem.setSizeHint(QtCore.QSize(200, 40))
        self.registerList.addItem(regItem)
        self.registerList.setItemWidget(regItem, reg)
        self.registers.append(regItem)

    def addPins(self):
        for port, dock in zip(self.ports, [self.palayout, self.pblayout, self.pclayout, self.pdlayout]):
            checkbox = dio.REGVALS(port)
            dock.addWidget(checkbox)
            self.btns[port] = checkbox

            seq = range(7, -1, -1)
            if port == 'C': seq = reversed(seq)  # PORTC pins are ordered top to bottom
            for a in seq:
                name = 'P' + port + str(a)
                checkbox = dio.widget(name, self.commandQ, extra=self.SPECIALS.get(name, ''))
                dock.addWidget(checkbox)
                self.btns[name] = checkbox

    def tabChanged(self, index):
        if self.userHexRunning:  # Firmware was running. Stop it.
            self.launchFirmwareButton.setChecked(False)
            self.jumpToApplication(False)

        if index != 0:  # examples/editor tab. disable monitoring
            self.monitoring = False
        else:  # Playground . enable monitoring and control.
            self.monitoring = True
            self.autoRefreshUserRegisters.setChecked(False)
            self.userRegistersAutoRefresh(False)
            self.setLogType('playground')

    def setLogType(self, tp):
        self.log.clear()
        if tp == 'playground':
            self.logLabel.setText("Monitor registers being read and set during each operation")
        elif tp == 'avr':
            self.logLabel.setText("Avr-Gcc compile/upload messages")
        elif tp == 'monitor':
            self.logLabel.setText("Monitor data input from the serial port")
        elif tp == 'python':
            self.logLabel.setText("Python Code operations monitor")

    ################USER CODE SECTION####################
    def codeOutput(self, filetype, filename):
        self.openCodeBreakupTab(filetype, filename)
        try:
            infile = open(filename, 'r')
            if filetype == 'list':
                self.listEditor.setPlainText(infile.read())
            if filetype == 'map':
                self.mapEditor.setPlainText(infile.read())
            if filetype == 'hex':
                self.hexEditor.setPlainText(infile.read())
            infile.close()
        except Exception as e:
            print(e)

    def openCodeBreakupTab(self, filetype, filename):
        tab = None
        if filetype == 'list':
            if self.listTab is None:
                self.openListTab()
            elif self.listTab.isHidden():
                self.codingTabs.addTab(self.listTab, "")
            tab = self.listTab
        elif filetype == 'map':
            if self.mapTab is None:
                self.openMapTab()
            elif self.mapTab.isHidden():
                self.codingTabs.addTab(self.mapTab, "")
            tab = self.mapTab
        elif filetype == 'hex':
            if self.hexTab is None:
                self.openHexTab()
            elif self.hexTab.isHidden():
                self.codingTabs.addTab(self.hexTab, "")
            tab = self.hexTab

        if tab != None:
            fname = filename.split
            self.codingTabs.setTabText(self.codingTabs.indexOf(tab), os.path.basename(filename))  # filetype + ":" +

    def openListTab(self):
        self.listTab = QtWidgets.QWidget()
        self.listTab.setObjectName("listTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.listTab)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listEditor = QtWidgets.QTextBrowser(self.listTab)
        self.listEditor.setObjectName("listEditor")
        self.verticalLayout.addWidget(self.listEditor)
        self.codingTabs.addTab(self.listTab, "")

    def openMapTab(self):
        self.mapTab = QtWidgets.QWidget()
        self.mapTab.setObjectName("mapTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.mapTab)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.mapEditor = QtWidgets.QTextBrowser(self.mapTab)
        self.mapEditor.setObjectName("mapEditor")
        self.verticalLayout_3.addWidget(self.mapEditor)
        self.codingTabs.addTab(self.mapTab, "")

    def openHexTab(self):
        self.hexTab = QtWidgets.QWidget()
        self.hexTab.setObjectName("hexTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.hexTab)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.hexEditor = QtWidgets.QTextBrowser(self.hexTab)
        self.hexEditor.setObjectName("hexEditor")
        self.verticalLayout_2.addWidget(self.hexEditor)
        self.codingTabs.addTab(self.hexTab, "")
        ico = QtGui.QIcon()
        ico.addPixmap(QtGui.QPixmap(":/control/hex.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.codingTabs.setTabIcon(self.codingTabs.indexOf(self.hexTab), ico)

    def appendLog(self, txt):
        self.log.append(txt)

    def appendLogPlain(self, txt):
        self.log.moveCursor(QtGui.QTextCursor.End)
        self.log.insertPlainText(txt.decode('ascii'))

    def configSerialGauge(self, val):
        if val == 0:  # 'byte'
            print('Byte Mode(0-255)')
            for a in self.serialGauge.gauges:
                a.set_MaxValue(255)
            self.serialGaugeConvert = 'bytes'
        if val == 1:  # 'ascii'
            print('ASCII(0-10000)')
            for a in self.serialGauge.gauges:
                a.set_MaxValue(10000)
            self.serialGaugeConvert = 'ascii'

    def setSerialgauge(self, vals):
        if self.serialGaugeConvert == 'bytes':
            self.serialGauge.setValue([vals[0]])
        elif self.serialGaugeConvert == 'ascii':
            self.serialStream += vals
            while b'\n' in self.serialStream:
                val, _, self.serialStream = self.serialStream.partition(b'\n')
                self.serialGauge.setValue([float(val)])

    def genLog(self):
        html = '''<table border="1" align="center" cellpadding="1" cellspacing="0" style="font-family:arial,helvetica,sans-serif;font-size:9pt;">
		<tbody><tr><td colspan="4">%s</td></tr>''' % (time.ctime())
        # html+='''<tr><td style="background-color:#77cfbb;">R/W</td><td style="background-color:#77cfbb;">REGISTER</td>
        # <td style="background-color:#77cfbb;">Value</td><td style="background-color:#77cfbb;">Hex/Binary</td></tr>'''

        for a in self.updatedRegs:
            row = self.updatedRegs[a]
            html += u'''
				<tr>
					<td>{0:s}</td>
					<td>{1:s}</td>
					<td>{2:d}</td>
					<td>0b{2:08b} | 0x{2:02x}</td>
				</tr>
				'''.format(u'W \u2193' if row[0] else u'R \u2191', a, row[1])
        html += "</tbody></table>"
        self.log.setHtml(html)

    def updateEverything(self):
        self.locateDevices()
        if not self.checkConnectionStatus(): return
        # KuttyPy monitor has handed over control to native code. act as serial monitor/ debug window
        if self.uploadingHex:
            return

        if self.userHexRunning:
            t = self.p.fd.read(self.p.fd.in_waiting)
            if len(t):
                self.serialGaugeSignal.emit(t)
                self.logThisPlain.emit(t)
            return

    ########################### UPLOAD HEX FILE #######################

    class uploadObject(QtCore.QObject):
        finished = QtCore.pyqtSignal()
        logThis = QtCore.pyqtSignal(str)
        resultSignal = QtCore.pyqtSignal(str, str)
        logThisPlain = QtCore.pyqtSignal(bytes)
        fname = ''
        p = None

        def __init__(self):
            super(AppWindow.uploadObject, self).__init__()

        def config(self, mode, p, fname):
            self.p = p
            self.fname = fname
            self.mode = mode

        def execute(self):
            global LKP
            if 'compile' in self.mode:
                try:
                    import subprocess
                    if self.fname[-2:] in ['.s', '.S']:
                        action = 'Assembl'
                    else:  # elif self.fname[-2:] in ['.c','.C']:
                        action = 'Compil'
                    fname = '.'.join(self.fname.split('.')[:-1])
                    if self.p.version == REGISTERS.VERSION_ATMEGA32 or self.p.connected == False:  # by default, compile for ATMEGA32.
                        # cmd = 'avr-gcc -Wall -O2 -mmcu=%s -o "%s" -Map "%s" "%s"' %('atmega32',fname,fname+'.map',self.fname)
                        cmd = 'avr-gcc -Wall -O2 -mmcu=%s -Wl,-Map="%s" -o "%s" "%s" %s' % (
                            'atmega32', fname + '.map', fname, self.fname, "-lkp" if LKP else "")  # includes MAP
                        self.logThis.emit('''<span style="color:#383;">%sing for Atmega32</span>''' % (action))
                    elif self.p.version == REGISTERS.VERSION_ATMEGA328P:
                        cmd = 'avr-gcc -Wall -O2 -mmcu=%s -o "%s" "%s"  %s' % (
                            'atmega328p', fname, self.fname, "-lkp" if LKP else "")
                        self.logThis.emit(
                            '''<span style="color:#383;">%sing for Atmega328p (Nano)</span>''' % (action))
                    else:
                        self.logThis.emit('''<span style="color:#222;">%ser UNAVAILABLE</span>''' % (action))
                        return
                    print(cmd)
                    res = subprocess.getstatusoutput(cmd)
                    if res[0] != 0:
                        self.logThis.emit('''<span style="color:#526;">%se Error: %s</span>''' % (
                            action, res[1].replace('\n', '<br>')))
                        self.finished.emit()
                        return

                    else:
                        self.logThis.emit('''<span style="color:gray;">%s</span><br>''' % res[1])

                    cmd = 'avr-objcopy -j .text -j .data -O ihex "%s" "%s.hex"' % (fname, fname)
                    res = subprocess.getstatusoutput(cmd)
                    self.logThis.emit(res[1])  # '''<span style="color:gray;">%s</span><br>'''%res[1])

                    cmd = 'avr-objdump -S "%s" > "%s.lst"' % (fname, fname)
                    res = subprocess.getstatusoutput(cmd)
                    self.logThis.emit(res[1])  # '''<span style="color:gray;">%s</span><br>'''%res[1])
                    self.logThis.emit(
                        'Finished %sing: Generated Hex File' % action)  # '''<span style="color:darkgreen;">Finished %sing: Generated Hex File</span>'''%(action))

                    self.resultSignal.emit('list', fname + '.lst')
                    self.resultSignal.emit('hex', fname + '.hex')
                    self.resultSignal.emit('map', fname + '.map')
                except Exception as err:
                    self.logThis.emit('''<span style="color:#d730ee;">Failed to %se:%s</span>''' % str(action, err))

            if self.p.connected:
                if 'upload' in self.mode:
                    try:
                        if self.fname[-2:] in ['.c', '.C', '.s', '.S']:
                            self.fname = self.fname[:-2] + '.hex'  # Replace .c with .hex
                        self.logThis.emit('''<span style="font-size:12pt">Upload Code... Trigger Reset...</span>''')
                        dude = uploader.Uploader(self.p.fd, hexfile=self.fname, logger=self.logThis)
                        self.p.fd.setRTS(0)
                        self.p.fd.setDTR(0)
                        time.sleep(0.002)
                        self.p.fd.setRTS(1)
                        self.p.fd.setDTR(1)
                        time.sleep(0.05)
                        dude.sync()
                        dude.program()
                        dude.verify()
                        self.p.fd.setRTS(0)
                        self.p.fd.setDTR(0)
                        time.sleep(0.01)
                        self.p.fd.setRTS(1)
                        self.p.fd.setDTR(1)
                        time.sleep(0.25)
                        self.p.get_version()
                        self.logThis.emit('''<span style="color:darkgreen;">Finished upload</span>''')
                    except Exception as err:
                        print('upload error', err)
                        self.p.fd.setRTS(0);
                        self.p.fd.setDTR(0);
                        time.sleep(0.01);
                        self.p.fd.setRTS(1);
                        self.p.fd.setDTR(1);
                        time.sleep(0.25)
                        self.p.get_version()
                        self.logThis.emit('''<span style="color:#d730ee;">Failed to upload</span>''')
            # self.jumpToApplication(False) #Force a reset
            self.finished.emit()

    def uploadHex(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, " Open a hex file to upload to your KuttyPy", "",
                                                         "Hex Files (*.hex)")
        if len(filename[0]):
            # self.userCode.setStyleSheet("border: 3px dashed #53ffff;")
            # self.tabs.setTabEnabled(0,False)
            self.uploadingHex = True
            self.log.clear()
            self.log.setText('''<span style="color:#225;">-- Uploading Code --</span><br>''')
            self.UploadObject.config('upload', self.p, filename[0])
            self.uploadThread.start()

    def openFile(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, " Open a C/Asm file to edit", self.defaultDirectory,
                                                         "C/ASM Files (*.c *.C *.s *.S *.h);; Asm Files (*.s *.S);; C Files (*.c *.C *.h)")
        if len(filename[0]):
            self.openFile_(filename[0])

    def openFile_(self, fname):
        for sourceTab in self.sourceTabs:
            print(self.sourceTabs[sourceTab][1], fname)
            if fname == self.sourceTabs[sourceTab][1]:  # File is already open
                self.activeSourceTab = sourceTab
                self.activeEditor = self.sourceTabs[sourceTab][0]
                self.CFile = self.sourceTabs[sourceTab][1]
                self.filenameLabel.setText(self.CFile)
                self.codingTabs.setCurrentIndex(self.codingTabs.indexOf(sourceTab))
                return

        if self.CFile is not None:  # A file is altready open
            self.addSourceTab()
        # self.defaultDirectory = ''
        self.filenameLabel.setText(fname)
        self.CFile = fname
        self.defaultDirectory = os.path.split(self.CFile)[0]
        self.sourceTabs[self.activeSourceTab][1] = self.CFile
        self.log.clear()
        infile = open(fname, 'r')
        self.activeEditor.setPlainText(
            infile.read())  # self.activeEditor = self.sourceTabs[self.activeSourceTab][0]
        infile.close()
        self.codingTabs.setTabText(self.codingTabs.indexOf(self.activeSourceTab), os.path.split(self.CFile)[1])
        self.log.setText('''<span style="color:#225;">-- Opened File: %s --</span><br>''' % fname)
        filetype = 'c'
        if self.CFile.endswith('.S') or self.CFile.endswith('.s'):
            filetype = 'asm'
        ico = QtGui.QIcon()
        ico.addPixmap(QtGui.QPixmap(f":/control/{filetype}.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.codingTabs.setTabIcon(self.codingTabs.indexOf(self.activeSourceTab), ico)
        self.updateWatcher()

    def updateWatcher(self):
        paths = []
        for sourceTab in self.sourceTabs:
            paths.append(self.sourceTabs[sourceTab][1])
        self.fs_watcher = QtCore.QFileSystemWatcher(paths)
        self.fs_watcher.fileChanged.connect(self.file_changed)
        print('updated watcher', paths)

    def file_changed(self, path):
        print('File Changed: %s' % path)
        self.reloadLabel.setText(path)
        self.reloadFrame.setVisible(True)

    def reloadFile(self):
        self.reloadFrame.setVisible(False)
        fname = self.reloadLabel.text()
        for sourceTab in self.sourceTabs:
            print(self.sourceTabs[sourceTab][1], fname)
            if fname == self.sourceTabs[sourceTab][1]:  # File is already open
                self.activeSourceTab = sourceTab
                self.activeEditor = self.sourceTabs[sourceTab][0]
                self.CFile = self.sourceTabs[sourceTab][1]
                self.filenameLabel.setText(self.CFile)
                self.codingTabs.setCurrentIndex(self.codingTabs.indexOf(sourceTab))
                self.defaultDirectory = os.path.split(self.CFile)[0]

                self.log.clear()
                infile = open(fname, 'r')
                self.activeEditor.setPlainText(
                    infile.read())  # self.activeEditor = self.sourceTabs[self.activeSourceTab][0]
                infile.close()
                self.log.setText('''<span style="color:#225;">-- Reloaded File: %s --</span><br>''' % fname)
                filetype = 'c'
                if self.CFile.endswith('.S') or self.CFile.endswith('.s'):
                    filetype = 'asm'
                ico = QtGui.QIcon()
                ico.addPixmap(QtGui.QPixmap(f":/control/{filetype}.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.codingTabs.setTabIcon(self.codingTabs.indexOf(self.activeSourceTab), ico)
                self.updateWatcher()
                return
        print(' Modified file is not open anymore', fname)

    def cancelReload(self):
        self.reloadFrame.setVisible(False)
        self.updateWatcher()

    def fontPlus(self):
        size = self.editorFont.pointSize()
        if size > 40: return
        self.editorFont.setPointSize(size + 1)
        self.updateFont()

    def fontMinus(self):
        size = self.editorFont.pointSize()
        if size < 5: return
        self.editorFont.setPointSize(size - 1)
        self.updateFont()

    def setFont(self, font):
        self.editorFont.setFamily(font)
        self.updateFont()

    def updateFont(self):
        for editors in self.sourceTabs:
            self.sourceTabs[editors][0].setFont(self.editorFont)
        if hasattr(self, 'hexEditor') and self.hexEditor is not None:
            self.hexEditor.setFont(self.editorFont)
        if hasattr(self, 'listEditor') and self.listEditor is not None:
            self.listEditor.setFont(self.editorFont)
        if hasattr(self, 'mapEditor') and self.mapEditor is not None:
            self.mapEditor.setFont(self.editorFont)

    def compileAndUpload(self):
        self.setLogType('avr')
        self.saveFile()
        if self.CFile:
            if self.userHexRunning:
                self.launchFirmwareButton.setChecked(False)
                self.jumpToApplication(False)
            self.uploadingHex = True
            self.log.setText('''<span style="color:#225;">-- Compiling and Uploading Code --</span><br>''')
            self.UploadObject.config('compileupload', self.p, self.CFile)
            self.uploadThread.start()

    def compile(self):
        self.setLogType('avr')
        self.saveFile()
        if self.CFile:
            self.log.setText('''<span style="color:green;">-- Compiling Code --</span><br>''')
            self.log.setText('''<span style="color:green;">-- %s --</span><br>''' % self.CFile)
            self.UploadObject.config('compile', self.p, self.CFile)
            self.uploadThread.start()

    def upload(self):
        self.setLogType('avr')
        if self.CFile:
            if self.userHexRunning:
                self.launchFirmwareButton.setChecked(False)
                self.jumpToApplication(False)
            self.uploadingHex = True
            self.log.setText('''<span style="color:green;">-- Uploading Code --</span><br>''')
            self.UploadObject.config('upload', self.p, self.CFile)
            self.uploadThread.start()

    def saveFile(self):
        if not self.CFile:
            self.CFile = self.saveAs()
            return
        if self.CFile is not None and len(self.CFile) > 1:
            self.updateWatcher()
            self.sourceTabs[self.activeSourceTab][1] = self.CFile
            self.activeEditor.markAsSaved(True)
            self.fs_watcher.removePath(self.CFile)
            fn = open(self.CFile, 'w')
            fn.write(self.activeEditor.toPlainText())
            fn.close()
            self.fs_watcher.addPath(self.CFile)
            self.codingTabs.setTabText(self.codingTabs.indexOf(self.activeSourceTab), os.path.split(self.CFile)[1])
            self.log.setText('''<span style="color:green;">-- Saved to: %s --</span><br>''' % self.CFile)
        else:
            self.log.setText('''<span style="color:#d730ee;">-- No File Selected --</span><br>''')

    def saveAs(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        print('created new file:', name)
        if len(name) > 0 and len(name[0]) > 1:
            self.CFile = name[0]
            self.filenameLabel.setText(self.CFile)
            self.log.setText('''<span style="color:green;">-- Created new file: %s --</span><br>''' % self.CFile)
            self.codingTabs.setTabText(self.codingTabs.indexOf(self.activeSourceTab), os.path.split(self.CFile)[1])
            self.saveFile()
            return self.CFile

    ##############################
    def setTheme(self, theme):
        self.setStyleSheet("")
        self.setStyleSheet(open(os.path.join(path["themes"], theme + ".qss"), "r").read())

    def initializeCommunications(self, port=False):
        if self.p:
            try:
                self.p.fd.close()
            except:
                pass
        if port:
            self.p = KuttyPyLib.connect(port=port)
        else:
            self.p = KuttyPyLib.connect(autoscan=True)

        if self.p.connected:
            self.VERSION = self.p.version
            self.launchFirmwareButton.setChecked(False)
            self.setWindowTitle('KuttyPy Integrated Development Environment [{0:s}]'.format(self.p.portname))

        else:
            self.setWindowTitle('KuttyPy Integrated Development Environment [ Hardware not detected ]')

    def setLanguage(self, lang='fr_FR'):
        translate(lang)
        self.retranslateUi(self)

    def showSerialGauge(self):
        self.serialGauge.show()

    def codeFinished(self):
        print('finished')
        self.uploadingHex = False

    def jumpToApplication(self, state):
        print('run firmware', state)
        if self.p:
            if state:
                self.serialFrame.show()
                self.userHexRunning = True
                self.p.fd.write(b'j')  # Skip to application (Bootloader resets)
                self.launchFirmwareButton.setText('Stop')

                self.setLogType('monitor')
                self.log.setText('''<span style="color:#004;">-- Serial Port Monitor --</span><br>''')
            # self.serialGauge.show()

            else:
                self.serialFrame.hide()
                self.p.fd.setRTS(0);
                self.p.fd.setDTR(0);
                time.sleep(0.01);
                self.p.fd.setRTS(1);
                self.p.fd.setDTR(1);
                time.sleep(0.2)
                while self.p.fd.in_waiting:
                    self.p.fd.read()
                self.p.get_version()
                self.userHexRunning = False
                self.launchFirmwareButton.setText('Run')
                # self.tabs.setEnabled(True)
                self.serialGauge.hide()
        else:
            if self.isChecked():
                self.setChecked(False)

    def sendASCII(self):
        s = self.serialData.text()
        self.p.fd.write(s.encode('utf-8'))

    def sendBinary(self):
        s = self.serialData.text()
        try:
            self.p.fd.write(chr(int(s) & 0xFF).encode('utf-8'))
        except Exception as e:
            print(e)

    def showServerStatus(self, msg):
        self.showStatus("Compiler: Error Launching Server (Restart app) ", True)
        QtWidgets.QMessageBox.warning(self, 'Server Error', msg)
        self.compile_thread_button.setText("Online Compiler")

    # self.statusBar.addPermanentWidget(self.compile_thread_button)

    def showStatus(self, msg, error=None):
        if error:
            self.statusBar.setStyleSheet("color:#633")
        else:
            self.statusBar.setStyleSheet("color:#333")
        self.statusBar.showMessage(msg)

    def locateDevices(self):
        try:
            L = KuttyPyLib.getFreePorts(self.p.portname)
        except Exception as e:
            print(e)
        total = len(L)
        menuChanged = False
        if L != self.shortlist:
            menuChanged = True
            if self.p.connected:
                if self.p.portname not in L:
                    self.setWindowTitle('Error : Device Disconnected')
                    QtWidgets.QMessageBox.warning(self, 'Connection Error',
                                                  'Device Disconnected. Please check the connections')
                    try:
                        self.p.close()
                    except:
                        pass
                    self.p.connected = False
                    self.setWindowTitle('KuttyPy Integrated Development Environment [ Hardware not detected ]')

            elif True in L.values():
                reply = QtWidgets.QMessageBox.question(self, 'Connection', 'Device Available. Connect?',
                                                       QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.initializeCommunications()

            # update the shortlist
            self.shortlist = L

    def checkConnectionStatus(self, dialog=False):
        if self.p.connected:
            return True
        else:
            if dialog: QtWidgets.QMessageBox.warning(self, 'Connection Error',
                                                     'Device not connected. Please connect a KuttyPy to the USB port')
            return False

    ######## WINDOW EXPORT SVG
    def exportSvg(self):
        from PyQt5 import QtSvg
        path, _filter = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '~/')
        if path:
            generator = QtSvg.QSvgGenerator()
            generator.setFileName(path)
            target_rect = QtCore.QRectF(0, 0, 800, 600)
            generator.setSize(target_rect.size().toSize())  # self.size())
            generator.setViewBox(self.rect())
            generator.setTitle("Your title")
            generator.setDescription("some description")
            p = QtGui.QPainter()
            p.begin(generator)
            self.render(p)
            p.end()


def translators(langDir, lang=None):
    """
    create a list of translators
    @param langDir a path containing .qm translation
    @param lang the preferred locale, like en_IN.UTF-8, fr_FR.UTF-8, etc.
    @result a list of QtCore.QTranslator instances
    """
    if lang == None:
        lang = QtCore.QLocale.system().name()
    result = []
    qtTranslator = QtCore.QTranslator()
    qtTranslator.load("qt_" + lang,
                      QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    result.append(qtTranslator)

    # path to the translation files (.qm files)
    sparkTranslator = QtCore.QTranslator()
    sparkTranslator.load(lang, langDir);
    result.append(sparkTranslator)
    return result


def firstExistingPath(l):
    """
    Returns the first existing path taken from a list of
    possible paths.
    @param l a list of paths
    @return the first path which exists in the filesystem, or None
    """
    for p in l:
        if os.path.exists(p):
            return p
    return None


def common_paths():
    """
    Finds common paths
    @result a dictionary of common paths
    """
    path = {}
    curPath = os.path.dirname(os.path.realpath(__file__))
    path["current"] = curPath
    sharedPath = "/usr/share/kuttypy"
    path["translation"] = firstExistingPath(
        [os.path.join(p, "lang") for p in
         (curPath, sharedPath,)])
    path["utilities"] = firstExistingPath(
        [os.path.join(p, 'utilities') for p in
         (curPath, sharedPath,)])

    path["templates"] = firstExistingPath(
        [os.path.join(p, 'utilities', 'templates') for p in
         (curPath, sharedPath,)])

    path["themes"] = firstExistingPath(
        [os.path.join(p, 'utilities', 'themes') for p in
         (curPath, sharedPath,)])

    path["examples"] = firstExistingPath(
        [os.path.join(p, 'examples') for p in
         (curPath, sharedPath,)])

    path["kpy"] = firstExistingPath(
        [os.path.join(p, 'kpy') for p in
         (curPath, sharedPath,)])

    path["blockly"] = firstExistingPath(
        [os.path.join(p, 'online', 'static') for p in
         (curPath, sharedPath,)])

    path["editor"] = firstExistingPath(
        [os.path.join(p, 'editor') for p in
         (curPath, sharedPath,)])

    lang = str(QtCore.QLocale.system().name())
    shortLang = lang[:2]
    return path


def run():
    global path, app, myapp
    path = common_paths()
    print('QT Version', QtWidgets.__file__)
    app = QtWidgets.QApplication(sys.argv)
    myapp = AppWindow(app=app, path=path)
    myapp.show()
    r = app.exec_()
    if myapp.compile_thread is not None:
        myapp.compile_thread.terminate()
        print('waiting to quit compile_thread')
        myapp.compile_thread.wait()

    app.deleteLater()
    sys.exit(r)


if __name__ == "__main__":
    run()
