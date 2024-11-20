'''
'''
# !/usr/bin/python3

import os, sys, time, re, traceback, platform
from typing import List

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import KuttyPyLib
import socket

from utilities.templates import ui_layout_visual as layout
from utilities import REGISTERS
from functools import partial

import constants
import inspect

class AppWindow(QtWidgets.QMainWindow, layout.Ui_MainWindow):
    p = None
    logThis = QtCore.pyqtSignal(str)
    showStatusSignal = QtCore.pyqtSignal(str, bool)
    serverSignal = QtCore.pyqtSignal(str)
    addMPSignal = QtCore.pyqtSignal()
    delMPSignal = QtCore.pyqtSignal()
    queryMPSignal = QtCore.pyqtSignal()
    cameraReadySignal = QtCore.pyqtSignal()

    logThisPlain = QtCore.pyqtSignal(bytes)
    codeOutput = QtCore.pyqtSignal(str, str)
    serialGaugeSignal = QtCore.pyqtSignal(bytes)
    serialGaugeConvert = 'bytes'
    serialStream = b''

    def __init__(self, parent=None, **kwargs):
        super(AppWindow, self).__init__(parent)

        self.external = None
        self.last_query_time = time.time()
        self.local_ip = 'localhost'
        self.setupUi(self)

        self.compile_thread = None
        self.mp_thread = None

        self.defaultDirectory = path["examples"]
        self.serverActive = False
        self.VERSION = REGISTERS.VERSION_ATMEGA32  # This needs to be dynamically changed when hardware is connected

        self.logThisPlain.connect(self.appendLogPlain)  # Connect to the log window

        self.statusBar = self.statusBar()
        self.makeBottomMenu()

        global app

        self.initializeCommunications()


        self.startTime = time.time()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateEverything)
        self.timer.start(20)

        # Auto-Detector
        self.shortlist = KuttyPyLib.getFreePorts()


    def addMP(self):
        from online.mp import HandLandmarkThread
        self.mpLabel.setVisible(True)
        self.mpLabel.resize(400, 300)

        self.last_query_time = time.time()
        if self.mp_thread is not None and self.mp_thread.isRunning():  #Available. ignore.
            self.mp_thread.ping()  # nudge
            pass
        else:
            self.mp_thread = HandLandmarkThread()
        self.mp_thread.setPriority(QThread.HighestPriority)
        self.mp_thread.change_pixmap_signal.connect(self.update_image)
        self.mp_thread.coordinates_signal.connect(self.compile_thread.updateCoords)
        self.mp_thread.dead_signal.connect(self.delMP)
        self.mp_thread.setCameraReadySignal(self.cameraReadySignal)
        self.mp_thread.start()

    def update_image(self, qt_image):
        """Update the QLabel with the new frame."""
        pixmap = QPixmap.fromImage(qt_image)
        self.mpLabel.setPixmap(pixmap)

    def closeEvent(self, event):
        """Ensure the thread is stopped when the dialog is closed."""
        event.ignore()
        print('closing...')

        if self.mp_thread is not None and self.mp_thread.isRunning:
            print('terminating camera...')
            self.mp_thread.terminate()
            self.mp_thread.wait()
            print('terminated.')
        event.accept()


    def delMP(self):
        print('closing MP window')
        if self.mp_thread is not None:
            self.mp_thread.running = False
        self.mpLabel.setVisible(False)

    def queryMP(self):
        if self.mp_thread is not None:
            self.mp_thread.ping()


    def makeBottomMenu(self):
        try:
            self.pushbutton.setParent(None)
        except:
            pass
        self.pushbutton = QtWidgets.QPushButton('Menu')
        self.pushbutton.setStyleSheet("color: #262;")
        menu = QtWidgets.QMenu()

        menu.addAction('PIP install mediapipe & CV', partial(self.showPipInstaller, 'mediapipe opencv-python-headless'))

        # Theme
        self.themeAction = QtWidgets.QWidgetAction(menu)
        themes = [a.split('.qss')[0] for a in os.listdir(path["themes"]) if '.qss' in a]
        self.themeBox = QtWidgets.QComboBox()
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
        #self.compile_thread_button.clicked.connect(self.activateCompileServer)
        self.statusBar.addPermanentWidget(self.compile_thread_button)

        self.bottomLabel = QtWidgets.QLabel("Messages")
        self.activateCompileServer()

        # Menu button
        self.statusBar.addPermanentWidget(self.pushbutton)

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
            self.compile_thread = create_server(self.showStatusSignal, self.serverSignal, path, self.local_ip,
                                                self.p)
            self.compile_thread.setAddMPSignal(self.addMPSignal)
            self.compile_thread.setDelMPSignal(self.delMPSignal)
            self.compile_thread.setQueryMPSignal(self.queryMPSignal)
            self.compile_thread.setCameraReadySignal(self.cameraReadySignal)

            self.showStatusSignal.connect(self.showStatus)
            self.serverSignal.connect(self.showServerStatus)
            self.addMPSignal.connect(self.addMP)
            self.delMPSignal.connect(self.delMP)
            self.queryMPSignal.connect(self.queryMP)
            s.close()
            self.showStatus("Visual Coding and Compiler Active at " + self.local_ip + ":8888", False)
            self.compile_thread_button.setText(self.local_ip)
            self.serverActive = True

    def showPipInstaller(self, name):
        from utilities.pipinstaller import PipInstallDialog
        self.pipdialog = PipInstallDialog(name, self)
        self.pipdialog.show()


    def appendLog(self, txt):
        self.log.append(txt)

    def appendLogPlain(self, txt):
        self.log.moveCursor(QtGui.QTextCursor.End)
        self.log.insertPlainText(txt.decode('ascii'))

    def updateEverything(self):
        self.locateDevices()
        if not self.checkConnectionStatus(): return


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
    if myapp.mp_thread is not None:
        myapp.mp_thread.stopRunning()

    if myapp.compile_thread is not None:
        myapp.compile_thread.stop_flask_app()
        myapp.compile_thread.terminate()
        if myapp.mp_thread is not None:
            myapp.mp_thread.running = False
            print('waiting to quit compile_thread')
        myapp.compile_thread.wait()

    app.deleteLater()
    sys.exit(r)


if __name__ == "__main__":
    run()
