'''
'''
# !/usr/bin/python3

import os
import platform
import socket
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5 import QtGui, QtCore, QtWidgets

from utilities import syntax
from utilities import texteditor
from utilities.templates import ui_layout_quiz as layout
from utilities.templates import ui_quiz_row

from utilities.quiz_server import create_server, connections


class ImageDialog(QtWidgets.QDialog):
    def __init__(self, image, parent=None):
        super(ImageDialog, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        # Create a QLabel to display the image
        self.imageLabel = QtWidgets.QLabel()
        layout.addWidget(self.imageLabel)

        # Convert the QImage to QPixmap and set it in the QLabel
        pixmap = QtGui.QPixmap.fromImage(image)
        self.imageLabel.setPixmap(pixmap)

        self.setWindowTitle("Image Dialog")


class QUIZROW(QtWidgets.QWidget, ui_quiz_row.Ui_Form):
    conn = None

    def __init__(self, parent, address, name, score, result):
        super(QUIZROW, self).__init__(parent)
        self.setupUi(self)
        self.setToolTip('IP:'+str(address[0]))
        self.nameLabel.setText(name)
        self.scoreLabel.setText(score)
        self.resultLabel.setText(result)

    def getscr(self):
        if self.conn is not None:
            print('get a screenshot')
            self.conn.send(b'SCREENSHOT\n')

class AppWindow(QtWidgets.QMainWindow, layout.Ui_MainWindow):
    p = None
    logThis = QtCore.pyqtSignal(str)
    showStatusSignal = QtCore.pyqtSignal(str, bool)
    serverSignal = QtCore.pyqtSignal(str,str)
    removeSignal = QtCore.pyqtSignal(str)
    imageSignal = QtCore.pyqtSignal(str,bytes)
    logThisPlain = QtCore.pyqtSignal(bytes)
    codeOutput = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None, **kwargs):
        super(AppWindow, self).__init__(parent)
        self.local_ip = ''
        self.setupUi(self)

        self.fs_watcher = None
        self.reloadFrame.setVisible(False)

        self.CFile = None  # '~/kuttyPy.c'
        self.defaultDirectory = path["questions"]
        # Define some keyboard shortcuts for ease of use

        ########## C CODE EDITOR SYNTAX HIGHLIGHTER
        self.code_highlighters = []
        ####### C CODE EDITOR #########
        self.codingTabs.tabCloseRequested.connect(self.closeCTab)
        self.codingTabs.tabBarClicked.connect(self.CTabChanged)

        self.activeEditor = None
        self.activeSourceTab = None
        self.sourceTabs = {}
        self.addSourceTab()

        self.statusBar = self.statusBar()
        self.makeBottomMenu()
        self.addFileMenu()
        self.addEditMenu()

        self.editorFont = QtGui.QFont()
        self.editorFont.setPointSize(12)
        self.editorFont.setFamily('Ubuntu mono')

        #self.MCAST_GRP = '234.0.0.1'
        #self.MCAST_PORT = 9999
        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        #self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 5))
        #self.sock.setsockopt(socket.SOL_IP, socket.SO_REUSEADDR, 1)
        #self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        ### self.sock.bind(("10.42.0.1", self.MCAST_PORT))
        #self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

        self.serverSignal.connect(self.registerResponse)
        self.imageSignal.connect(self.registerScreenshot)
        self.removeSignal.connect(self.removeClient)
        self.addSourceTab()
        self.activeEditor.setPlainText('Q1\nA1\nA2\nA3\nA3\nANSWER: 2')

        self.responses = {}  # List of responses
        self.clients = []
        self.activateQuizListener()

        self.MAX_COLUMNS = 4
        self.response_row = 0
        self.response_column = 0

        #self.addDummies()
        global app

    def connectServer(self):
        pass

    def addDummies(self):
        for a in range(20):
            row = QUIZROW(self,'hi'+str(a),'----', '---', '--------')
            self.responsesLayout.addWidget(row,self.response_row,self.response_column)
            self.responses[id] = row
            self.response_column+=1
            if self.response_column>self.MAX_COLUMNS:
                self.response_column = 0
                self.response_row+=1

    def closeEvent(self, event):
        self.external.terminate()
        self.external.waitForFinished(1000)

    def embedTerminal(self):
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

    def removeClient(self,addr):
        print(addr, ' left')
        try:
            row = self.responses[addr]
            self.responsesLayout.removeWidget(row)
            self.responses.pop(addr)
        except Exception as e:
            print(e)

    def registerResponse(self, addr, msg):
        print('got',msg)
        if addr not in self.clients:
            self.clients.append(addr)
        '''
        if addr == 'ERROR':
            self.termFrame.setStyleSheet('background: #f00;')
            l = QtWidgets.QLabel(msg)
            self.responsesLayout.addWidget(l)
            return
        '''
        name,res = msg.split(':')
        score, responses = res.split('\t')
        id = addr
        if id not in self.responses:
            row = QUIZROW(self,addr,name, score, responses)
            self.responsesLayout.addWidget(row,self.response_row,self.response_column)
            self.responses[id] = row
            print(connections)
            self.responses[id].conn = connections[id]
            self.response_column+=1
            if self.response_column>self.MAX_COLUMNS:
                self.response_column = 0
                self.response_row+=1

        else:
            row = self.responses[id]
            row.scoreLabel.setText(score)
            row.resultLabel.setText(responses)
            row.nameLabel.setText(name+'|'+addr)

    def registerScreenshot(self, addr, msg):
        if addr in self.responses:
            row = self.responses[addr]
            print('fetched screenshot:', len(msg))
            image = QtGui.QImage()
            image.loadFromData(QtCore.QByteArray(msg))
            # Create and show the ImageDialog
            dialog = ImageDialog(image)
            dialog.exec_()

    def activateQuizListener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)  # Set a timeout to avoid blocking indefinitely
        s.connect(("8.8.8.8", 80))  # Connect to a public IP address
        self.local_ip = s.getsockname()[0]
        self.ipLabel.setText('IP: '+self.local_ip)

        self.quiz_thread = create_server(self.showStatusSignal, self.serverSignal, self.removeSignal, self.imageSignal, self.local_ip)
        self.showStatusSignal.connect(self.showStatus)
        s.close()
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

        self.bottomLabel = QtWidgets.QLabel("Messages")

        # Menu button
        self.statusBar.addPermanentWidget(self.pushbutton)

    def closeCTab(self, index):
        print('Close Tab', index)
        widget = self.codingTabs.widget(index)
        sourceTabClosed = False
        if len(self.sourceTabs) == 1:
            print("last tab. won't close.")
            return
        else:
            print('closing source tab', widget.objectName())
            self.sourceTabs.pop(widget)
            sourceTabClosed = True

        self.codingTabs.removeTab(index)
        if sourceTabClosed:  # Source Tab closed. Re-assign active source tab
            self.activeSourceTab = list(self.sourceTabs.keys())[0]
            self.activeEditor = self.sourceTabs[self.activeSourceTab][0]
            self.CFile = self.sourceTabs[self.activeSourceTab][1]
            self.codingTabs.setCurrentIndex(self.codingTabs.indexOf(self.activeSourceTab))
            print('New Source Tab:', self.getActiveFilename(), self.CFile)

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
            print('Change Tab', index, self.codingTabs.tabText(index), self.CFile)

    def openFile(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, " Open a text file to edit", self.defaultDirectory,
                                                         "Text Files (*.txt *.TXT)")
        if len(filename[0]):
            self.openFile_(filename[0])

    def openFile_(self, fname):
        for sourceTab in self.sourceTabs:
            print(self.sourceTabs[sourceTab][1], fname)
            if fname == self.sourceTabs[sourceTab][1]:  # File is already open
                self.activeSourceTab = sourceTab
                self.activeEditor = self.sourceTabs[sourceTab][0]
                self.CFile = self.sourceTabs[sourceTab][1]
                self.codingTabs.setCurrentIndex(self.codingTabs.indexOf(sourceTab))
                return

        if self.CFile is not None:  # A file is altready open
            self.addSourceTab()
        # self.defaultDirectory = ''
        self.CFile = fname
        self.defaultDirectory = os.path.split(self.CFile)[0]
        self.sourceTabs[self.activeSourceTab][1] = self.CFile
        infile = open(fname, 'r')
        self.activeEditor.setPlainText(
            infile.read())  # self.activeEditor = self.sourceTabs[self.activeSourceTab][0]
        infile.close()
        self.codingTabs.setTabText(self.codingTabs.indexOf(self.activeSourceTab), os.path.split(self.CFile)[1])
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
                self.codingTabs.setCurrentIndex(self.codingTabs.indexOf(sourceTab))
                self.defaultDirectory = os.path.split(self.CFile)[0]

                infile = open(fname, 'r')
                self.activeEditor.setPlainText(
                    infile.read())  # self.activeEditor = self.sourceTabs[self.activeSourceTab][0]
                infile.close()
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

    def upload(self):
        print('upload')
        '''
        for a in self.responses:
            self.responsesLayout.removeWidget(self.responses[a])
            self.responses[a].setParent(None)
        self.responses = {}
        self.response_row=0
        self.response_column=0
        '''
        for id in self.responses:
            row = self.responses[id]
            row.scoreLabel.setText('0/0')
            row.resultLabel.setText('---')

        dat = self.activeEditor.toPlainText()
        print(connections)
        for ip in connections:
            try:
                connections[ip].send(('QUIZ'+chr(1)+dat.replace('\n',chr(1))+'\n').encode('utf-8'))
            except Exception as e:
                connections.pop(ip)
                print(type(ip), e)
        #self.quiz_thread.sendQuestions()
        #self.sock.sendto(dat, (self.MCAST_GRP, self.MCAST_PORT)) # no multicast for now.
        '''
        for a in self.clients:
            try:
                s = socket.socket()
                s.connect((a, 9090))
                s.send(dat)
                s.close()
            except Exception as e:
                print(e)
            '''

    def saveFile(self):
        if not self.CFile:
            self.CFile = self.saveAs()
        if self.CFile is not None and len(self.CFile) > 1:
            self.sourceTabs[self.activeSourceTab][1] = self.CFile
            self.activeEditor.markAsSaved(True)
            self.fs_watcher.removePath(self.CFile)
            fn = open(self.CFile, 'w')
            fn.write(self.activeEditor.toPlainText())
            fn.close()
            self.fs_watcher.addPath(self.CFile)
            self.codingTabs.setTabText(self.codingTabs.indexOf(self.activeSourceTab), os.path.split(self.CFile)[1])

    def saveAs(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        print('created new file:', name)
        if len(name) > 0 and len(name[0]) > 1:
            self.CFile = name[0]
            self.codingTabs.setTabText(self.codingTabs.indexOf(self.activeSourceTab), os.path.split(self.CFile)[1])
            self.saveFile()
            return self.CFile

    ##############################
    def setTheme(self, theme):
        self.setStyleSheet("")
        self.setStyleSheet(open(os.path.join(path["themes"], theme + ".qss"), "r").read())

    def showStatus(self, msg, error=None):
        if error:
            self.statusBar.setStyleSheet("color:#633")
        else:
            self.statusBar.setStyleSheet("color:#333")
        self.statusBar.showMessage(msg)

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

    path["questions"] = firstExistingPath(
        [os.path.join(p, 'questions') for p in
         (curPath, sharedPath,)])

    path["kpy"] = firstExistingPath(
        [os.path.join(p, 'kpy') for p in
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
    '''
    if myapp.compile_thread is not None:
        myapp.compile_thread.terminate()
        print('waiting to quit compile_thread')
        myapp.compile_thread.wait()
    '''

    app.deleteLater()
    sys.exit(r)


if __name__ == "__main__":
    run()
