# -*- coding: utf-8; mode: python; indent-tabs-mode: t; tab-width:4 -*-
import functools

import os, sys, time, re, traceback, platform , os.path
from PyQt5 import QtGui, QtCore, QtWidgets
import KuttyPyLib

import sys, time, tempfile, json, socket

from utilities.widgetUtils import MyRow, MyExptRow
import numpy as np
import eyes17.eyemath17 as em
from functools import partial
import json
from utilities.templates import ui_blockly_layout, syntax

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMessageBox


class webPage(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        super(webPage, self).__init__()
        self.featurePermissionRequested.connect(self.onFeaturePermissionRequested)

    def javaScriptConsoleMessage(self, level, msg, line, source):
        print(' \033[4;33m line %d: %s !! %s , %s \033[0m' % (line, msg, source, level))

    def onFeaturePermissionRequested(self, url, feature):
        print('feature requested', feature)
        if feature in (QWebEnginePage.MediaAudioCapture,
                       QWebEnginePage.MediaVideoCapture,
                       QWebEnginePage.MediaAudioVideoCapture,
                       QWebEnginePage.DesktopVideoCapture,
                       QWebEnginePage.DesktopAudioVideoCapture):
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)

    def certificateError(self, certificateError):
        certificateError.isOverridable()
        certificateError.ignoreCertificateError()
        return True


class webWin(QWebEngineView):
    def closeEvent(self, e):
        """
		Sends a message to self.parent to tell that the checkbox for
		the help window should be unchecked.
		"""
        print('leaving...')
        return

    def setLocalXML(self, fname):
        self.handler.setLocalXML(fname)

    def __init__(self, parent, name='', lang="en"):
        """
		Class for the help window
		:param parent: this is the main window
		:param name: a tuple (title, HTML file indication)
		name[1] can be either a simple string or another iterable. When it is
		a simple string, it means that the file to open is in htm/<name>.html;
		on the contrary, name[1] is a list of file names, without their
		.html suffix, to be searched in a list of directories; the first
		hit during the search defines the file to open.
		:param lang: the desired language
		"""

        QWebEngineView.__init__(self)

        self.parent = parent
        self.p = self.parent.p
        self.lang = lang
        self.mypage = webPage(self)
        self.setPage(self.mypage)

        try:
            from PyQt5.QtWebChannel import QWebChannel
            self.channel = QWebChannel()
            self.handler = self.dataHandler(self.parent)
            self.channel.registerObject('backend', self.handler)

            self.hwhandler = self.HWHandler(self.parent)
            self.channel.registerObject('hwbackend', self.hwhandler)

            self.page().setWebChannel(self.channel)

            fn = os.path.join(self.parent.blocksPath, 'webview.html')

            self.load(QtCore.QUrl.fromLocalFile(fn))
            self.setWindowTitle(self.tr('Block Coding: %s') % fn)


        except Exception as e:
            print(e)

    class dataHandler(QtCore.QObject):
        def __init__(self, parent):
            QtWidgets.QMainWindow.__init__(self)
            self.parent = parent
            self.local_xml = ''
            self.openFileWriters = {}
            self.MCAST_GRP = '234.0.0.1'
            self.MCAST_PORT = 9999
            self.MULTICAST_TTL = 2
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.MULTICAST_TTL)

        def setLocalXML(self, fname):
            self.local_xml = open(fname).read()
            print('newlocal xml from', fname)

        @QtCore.pyqtSlot(str)
        def updateCode(self, code):
            code = "from kuttyPy import *\n\n" + code
            self.parent.editor.setPlainText(code)

        @QtCore.pyqtSlot(str, bool)
        def xmlCode(self, code, bcast):
            if bcast:
                self.sock.sendto(code.encode(), (self.MCAST_GRP, self.MCAST_PORT))

        @QtCore.pyqtSlot()
        def startStepBroadcast(self):
            self.sock.sendto("!+".encode(), (self.MCAST_GRP, self.MCAST_PORT))

        @QtCore.pyqtSlot()
        def offBroadcast(self):
            self.sock.sendto("!-".encode(), (self.MCAST_GRP, self.MCAST_PORT))

        @QtCore.pyqtSlot(str, str)
        def saveXML(self, name, code):
            import shelve
            shelf = shelve.open(name)
            shelf['kuttypycode'] = code
            shelf.close()
            print('wrote', name)

        @QtCore.pyqtSlot(str, str)
        def saveXMLtoDisc(self, name, code):
            name = QtWidgets.QFileDialog.getSaveFileName(self.parent, 'Save File', QtCore.QDir.currentPath() , 'XML(*.xml)')
            print('created new file:', name)
            if len(name) > 0 and len(name[0]) > 1:
                fname= name[0]
                if not ('.xml' in fname or '.XML' in fname):
                    fname += '.xml'
                fn = open(fname, 'w')
                fn.write(code)
                fn.close()

        @QtCore.pyqtSlot()
        def openFileDialog(self):
            filename = QtWidgets.QFileDialog.getOpenFileName(self.parent, " Open an XML program", "~",
                                                             "XML Files (*.xml *.XML)")
            if len(filename[0]):
                self.parent.web.setLocalXML(filename[0])
                self.parent.filenameLabel.setText(filename[0])
                self.parent.web.mypage.runJavaScript("JSBridge.loadLocalXML('local_opened_file',loadRawXml);")


        @QtCore.pyqtSlot()
        def closeFiles(self):
            for a in self.openFileWriters:
                try:
                    a.close()
                except:
                    pass
            self.openFileWriters = {}


        @QtCore.pyqtSlot(str)
        def fileopen(self, fname):
            if fname not in self.openFileWriters:
                self.openFileWriters[fname] = open(os.path.join(os.path.expanduser('~'), fname), 'wt')
                print('open file', fname, self.openFileWriters[fname])

        @QtCore.pyqtSlot(str, str)
        def writeToFile(self, fname, data):
            if fname not in self.openFileWriters:
                self.openFileWriters[fname] = open(os.path.join(os.path.expanduser('~'), fname), 'wt')
            self.openFileWriters[fname].write(data)

        @QtCore.pyqtSlot(str, str, str, str, str)
        def save_lists(self, fname, x, y1, y2, y3):
            print('not implemented')

        @QtCore.pyqtSlot(str, result=str)
        def loadLocalXML(self, tp):
            if (tp == 'local_opened_file'):
                return self.local_xml
            import shelve
            shelf = shelve.open(tp)
            return shelf['kuttypycode']

        @QtCore.pyqtSlot(str, result=list)
        def loadXMLFile(self, tp):

            return ['''
 <xml xmlns="https://developers.google.com/blockly/xml">
      <block type="controls_repeat_ext" id="Mm^6|oM;+Z@e){tU@H-D" x="16" y="66">
        <value name="TIMES">
          <shadow type="math_number" id="FS)@SW9w!grBo$PN?kc2">
            <field name="NUM">10</field>
          </shadow>
        </value>
        <statement name="DO">
          <block type="wait_seconds" id="r#H-^Lg}:/JeUrdUE[b0">
            <field name="SECONDS">0.1</field>
            <next>
              <block type="cs_print" id="^c7PQB~?I3$6`}cI(YL]">
                <value name="TEXT">
                  <shadow type="text" id="S;Wo(5qr^XD=T+Q!ho1-">
                    <field name="TEXT">abc</field>
                  </shadow>
                  <block type="get_voltage" id="^qjm6WY}9*Q/I{1Yje*]">
                    <field name="CHANNEL">A0</field>
                  </block>
                </value>
                <next>
                  <block type="wait_seconds" id="9#4w,dJu*TuT7P)Ouo+R">
                    <field name="SECONDS">0.1</field>
                  </block>
                </next>
              </block>
            </next>
          </block>
        </statement>
      </block>
    </xml>
			''']

        @QtCore.pyqtSlot(str, str, result=str)
        def fourier_transform(self, xin, yin):
            x = json.loads(xin)
            v = json.loads(yin)
            dt = x[1] - x[0]
            try:
                xa, ya = em.fft(np.array(v), dt)
                # peak = self.peak_index(xa,ya)
                # ypos = np.max(ya)
                # pop = pg.plot(xa,ya, pen = self.traceCols[ch])
                return json.dumps([xa.tolist(), ya.tolist()])
            except Exception as err:
                print('FFT error:', err)
            return json.dumps([[], []])

        @QtCore.pyqtSlot(str, str, int, result=float)
        def sine_fit_arrays(self, xa, ya, p):
            x = json.loads(xa)
            y = json.loads(ya)
            try:
                yfit, fa = em.fit_sine(np.array(x), np.array(y))
                if (p == 0):
                    return fa[0]
                elif (p == 1):
                    return fa[1] * 1000
                elif (p == 2):
                    return 180 * fa[2] / np.pi
            except Exception as err:
                print('fit_sine error:', err)
            return 0

        @QtCore.pyqtSlot(str, str, str, str, int, result=float)
        def sine_fit_two_arrays(self, xa, ya, xa2, ya2, p):
            x = json.loads(xa)
            y = json.loads(ya)
            x2 = json.loads(xa2)
            y2 = json.loads(ya2)
            try:
                yfit, fa = em.fit_sine(np.array(x), np.array(y))
                yfit2, fa2 = em.fit_sine(np.array(x2), np.array(y2))
                if (p == 0):  # Amp ratio (Gain)
                    if (fa[0] > 0):
                        return fa2[0] / fa[0]
                elif (p == 1):  # Freq ratio (X)
                    if (fa[1] > 0):
                        return fa2[1] / fa[1]
                elif (p == 2):  # Phase difference
                    return 180 * (fa2[2] - fa[2]) / np.pi
            except Exception as err:
                print('fit_sine2 error:', err)
            return 0

    class HWHandler(QtCore.QObject):
        def __init__(self, parent):
            QtWidgets.QMainWindow.__init__(self)
            self.p = parent.p
            self.parent = parent
            self.active_sensors = {}

        def reconfigure(self, p):
            self.p = p

        @QtCore.pyqtSlot(int, result=float)
        def get_voltage(self, chan):
            return self.p.readADC(chan)

        @QtCore.pyqtSlot(str, int)
        def set_reg(self, reg, data):
            self.p.setReg(reg, data)
        @QtCore.pyqtSlot(str, result=int)
        def get_reg(self, reg):
            return self.p.getReg(reg)


        @QtCore.pyqtSlot(result=bool)
        def get_device_status(self):
            if self.p != None:
                return self.p.connected
            else:
                return False

        @QtCore.pyqtSlot()
        def programStarting(self):
            return

        @QtCore.pyqtSlot(str, str, result=float)
        def get_sensor(self, sensor, param):
            return self.p.get_sensor(sensor, int(param))


        @QtCore.pyqtSlot(int, bool, float)
        def stepper_move(self, steps, dir, delay):
            self.p.stepper_move(steps, dir, delay)

        @QtCore.pyqtSlot(result=str)
        def getAllSensors(self):
            sensors=[]
            for addr in self.p.addressmap:
                sensors.append('['+str(addr)+']'+self.p.addressmap[addr])
            print('getAllSensors',self.p.addressmap,sensors)
            return json.dumps(sensors)

        @QtCore.pyqtSlot(result=str)
        def scanI2C(self):
            sensors = []
            self.active_sensors={} # Empty sensors list. forces re-init for everyone
            x = self.p.I2CScan()
            print('Responses from: ', x)
            for a in x:
                possiblesensors = self.p.sensormap.get(a, None)
                if len(possiblesensors) > 0:
                    for sens in possiblesensors:
                        s = self.p.namedsensors.get(sens)
                        sensors.append('[' + str(a) + ']' + s['name'].split(' ')[0])
                        continue
            print('found', sensors)
            return json.dumps(sensors)

        @QtCore.pyqtSlot(str, result=str)
        def getSensorParameters(self, name):
            print('found sensor params for', name)
            return json.dumps(self.p.namedsensors[name]["fields"])

        @QtCore.pyqtSlot(str,int, result=str)
        def get_generic_sensor(self, name,addr):
            if name not in self.active_sensors:
                self.active_sensors[name] = self.p.namedsensors[name]
                self.p.namedsensors[name]['init'](address=addr)
            return json.dumps(self.active_sensors[name]['read']())


        @QtCore.pyqtSlot(int)
        def set_gmcounter_voltage(self, value):
            self.p.CSGM_config(int(value))

        @QtCore.pyqtSlot(float)
        def gmcounter_timelimit(self, value):
            self.p.CSGM_timelimit(value)
        @QtCore.pyqtSlot()
        def start_gmcounter(self):
            self.p.CSGM_start()
        @QtCore.pyqtSlot()
        def stop_gmcounter(self):
            self.p.CSGM_stop()



def load_project_structure(startpath, tree):
    """
	Load Project structure tree
	:param startpath: 
	:param tree: 
	:return: 
	"""

    import os
    from PyQt5.QtWidgets import QTreeWidgetItem
    from PyQt5.QtGui import QIcon
    for element in os.listdir(startpath):
        path_info = startpath + "/" + element
        if os.path.isdir(path_info):
            parent_itm = QTreeWidgetItem(tree, [os.path.basename(element)])
            load_project_structure(path_info, parent_itm)
            parent_itm.setIcon(0, QIcon(os.path.join(startpath, element + '.jpg')))
        else:
            name = os.path.basename(element)
            if (name.endswith('.jpeg')):
                parent_itm = QTreeWidgetItem(tree, [os.path.basename(element.replace('.jpeg', '.xml'))])
                parent_itm.setIcon(0, QIcon(os.path.join(startpath, element)))
            elif (name.endswith('.xml')):
                parent_itm = QTreeWidgetItem(tree, [os.path.basename(element)])


class Expt(QtWidgets.QWidget, ui_blockly_layout.Ui_Form):
    def __init__(self, **kwargs):
        super(Expt, self).__init__()
        self.setupUi(self)
        self.subcatScroll.setVisible(False)
        self.samplepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blockly/samples")
        if os.path.exists(self.samplepath):
            self.thumbnailpath = os.path.join(self.samplepath, "thumbs")

            try:
                self.setStyleSheet(open(os.path.join(os.path.dirname(__file__), "layouts/style.qss"), "r").read())
            except Exception as e:
                print('stylesheet missing. ', e)
            self.p = None  # connection to the device hardware

            self.blocksPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blockly')
            self.web = webWin(self, 'block coding')
            self.webLayout.addWidget(self.web)

            self.highlight = syntax.PythonHighlighter(self.editor.document())
            self.editorFont = QtGui.QFont()
            self.editorFont.setPointSize(10)

            # load_project_structure(self.samplepath, self.directoryBrowser)
            with open(os.path.join(self.samplepath, 'experiments.json')) as expts:
                self.expts = json.loads(expts.read())

            print(self.expts)

            # load_project_structure(self.samplepath, self.thumbnailpath, self.directoryBrowser)
            self.load_categories(self.samplepath, self.thumbnailpath, self.expts)

            # Auto-Detector
            self.shortlist = KuttyPyLib.getFreePorts()
            self.initializeCommunications()

        else:
            QMessageBox.warning(None,
                                self.tr("Blockly is missing"),
                                self.tr("""\
You wanted to launch the blockly plugin.
Unfortunately the plugin is missing... Consider
installing it (it is a non-free package)."""))

        self.themetimer = QtCore.QTimer()
        self.themetimer.setSingleShot(True)
        self.themetimer.timeout.connect(functools.partial(self.setTheme,'visual_styles'))
        self.themetimer.start(100)
        #self.setTheme('visual_styles')

        self.startTime = time.time()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.locateDevices)
        self.timer.start(500)

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
            self.web.hwhandler.reconfigure(self.p)
            self.setWindowTitle('KuttyPy Visual Programming Environment [{0:s}]'.format(self.p.portname))

        else:
            self.setWindowTitle('KuttyPy Visual Programming Environment [ Hardware not detected ]')

    def locateDevices(self):
        L=[]
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


            # updatex the shortlist
            self.shortlist = L

    def checkConnectionStatus(self, dialog=False):
        if self.p.connected:
            return True
        else:
            if dialog: QtWidgets.QMessageBox.warning(self, 'Connection Error',
                                                     'Device not connected. Please connect a KuttyPy to the USB port')
            return False

    def showDirectory(self):
        self.directoryBrowser.setVisible(True)

    def setTheme(self, theme):
        #self.setStyleSheet("")
        self.setStyleSheet(open(os.path.join(self.samplepath, theme + ".qss"), "r").read())
        print('Theme set to ', os.path.join(self.samplepath, theme + ".qss"))

    def load_categories(self, startpath, thumbpath, exptjson):
        for cat in exptjson:
            catdeets = exptjson[cat]
            name = catdeets['image'].split('.')[0]
            clickevent = partial(self.load_subcategory, startpath, catdeets['files'], catdeets['directory'])
            catrow = MyRow(name, catdeets['description'], os.path.join(startpath, catdeets['image']),
                           catdeets['directory'], clickevent)
            self.categoryLayout.addWidget(catrow)

    exptCards = []
    activeCategory = None

    def load_subcategory(self, startpath, files, directory, ev):
        self.setTheme('visual_styles')

        if (directory == self.activeCategory):
            self.activeCategory = None
            self.subcatScroll.setVisible(False)
        else:
            self.subcatScroll.setVisible(True)
            self.activeCategory = directory

        for a in self.exptCards:
            self.subcategoryLayout.removeWidget(a)
        self.exptCards = []
        self.subcategoryLabel.setText(directory)
        for name in files:
            desc = files[name]
            fname = name + '.xml'
            # name = fname.split('.')[0].replace(' ','_') #Replace spaces with _ for python files.
            clickevent = partial(self.loadExample, os.path.join(startpath, directory, name))
            catrow = None
            for extension in ['.jpg', '.jpeg', '.png']:
                if os.path.exists(os.path.join(self.thumbnailpath, name + extension)):
                    catrow = MyExptRow(name, desc, os.path.join(self.thumbnailpath, name + extension), directory,
                                       clickevent)
                    break
            if catrow is None:
                for extension in ['.jpg', '.jpeg', '.png']:
                    if os.path.exists(os.path.join(self.samplepath, directory, name + extension)):
                        catrow = MyExptRow(name, desc, os.path.join(self.samplepath, directory, name + extension),
                                           directory, clickevent)
                        break

            if catrow is None:
                print('No thumb found.', name)
                catrow = MyExptRow(name, desc, None, directory,
                                   clickevent)  # os.path.join(self.samplepath, directory, name + extension)

            if (catrow is not None):
                self.subcategoryLayout.addWidget(catrow)
                self.exptCards.append(catrow)

    def loadExample(self, item, ev):
        self.activeCategory = None
        self.subcatScroll.setVisible(False)
        self.web.setLocalXML(item + '.xml')
        self.filenameLabel.setText(item + '.xml')

        self.web.mypage.runJavaScript("JSBridge.loadLocalXML('local_opened_file',loadRawXml);")

    def fontPlus(self):
        size = self.editorFont.pointSize()
        if size > 40: return
        self.editorFont.setPointSize(size + 1)
        self.editor.setFont(self.editorFont)

    def fontMinus(self):
        size = self.editorFont.pointSize()
        if size < 5: return
        self.editorFont.setPointSize(size - 1)
        self.editor.setFont(self.editorFont)

    def setFont(self, font):
        self.editorFont.setFamily(font)
        self.editor.setFont(self.editorFont)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # translation stuff
    lang = QtCore.QLocale.system().name()
    t = QtCore.QTranslator()
    t.load("lang/" + lang, os.path.dirname(__file__))
    app.installTranslator(t)
    t1 = QtCore.QTranslator()
    t1.load("qt_" + lang,
            QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(t1)

    mw = Expt(app=app)
    mw.show()
    sys.exit(app.exec_())
