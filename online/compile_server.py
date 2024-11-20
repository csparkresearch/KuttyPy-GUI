import typing

import numpy as np
from flask import Flask, request, Blueprint, jsonify
import logging
from flask_cors import CORS
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QEventLoop
from PyQt5.QtWidgets import QApplication

# blueprint for socket comms parts of app
from .compile_routes import main as main_blueprint, local_ip
from .compile_routes import setStatusSignal, setKpyPath
from .blockly_routes import bly as blockly_blueprint
#from .blockly_mp_routes import blymp as blockly_mediapipe_blueprint
from .blockly_routes import setBlocklyPath, setP
from werkzeug.serving import make_server, WSGIRequestHandler
import threading, webbrowser

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple


print('starting the compile server...')

flask_thread = None
server_ip = ''
device = None


def create_server(showStatusSignal, serverSignal, paths, local_ip, dev):
	global flask_thread, server_ip, device
	server_ip = local_ip
	setStatusSignal(showStatusSignal)
	setKpyPath(paths['kpy'], local_ip)
	setBlocklyPath(paths['blockly'], local_ip)
	device = dev
	setP(dev)
	flask_thread = FlaskThread()
	flask_thread.setServerSignal(serverSignal)
	# flask_thread.finished.connect(QApplication.quit)

	# Start the thread
	flask_thread.start()
	return flask_thread


class QuietRequestHandler(WSGIRequestHandler):
    def log(self, type, message, *args):
        pass  # Disable the logging

class FlaskThread(QThread):
	finished = pyqtSignal()
	serverSignal = None
	MPSlots= None


	def __init__(self, parent=None):
		super().__init__(parent)
		self.cameraReadySignal = None
		self.coords = None
		self.delMPSignal = None
		self.addMPSignal = None
		self.queryMPSignal = None
		self.server = None

	def setAddMPSignal(self,sig):
		self.addMPSignal = sig

	def setDelMPSignal(self,sig):
		self.delMPSignal = sig

	def setQueryMPSignal(self, sig):
		self.queryMPSignal = sig

	def setCameraReadySignal(self, sig):
		self.cameraReadySignal = sig

	def setServerSignal(self, sig):
		self.serverSignal = sig

	def open_browser(self):
		state = 'false'
		if device is not None:
			if device.connected:
				state = 'true'

		if len(server_ip)>0:
			webbrowser.open(f"http://{server_ip}:8888/visual" + '?connected='+state)  # Adjust the URL as needed
		else:
			webbrowser.open(f"http://localhost:8888/visual"+ '?connected='+state)  # Adjust the URL as needed

	def run(self):
		# Run the Flask app in a separate thread
		print('starting the flask app...')
		self.app = Flask(__name__, template_folder='flask_templates', static_folder='static', static_url_path='/')
		self.app.logger.setLevel(logging.WARNING)
		CORS(self.app)
		self.app.register_blueprint(main_blueprint)
		self.app.register_blueprint(blockly_blueprint)
		self.app.register_blueprint(self.construct_mp_blueprint(), )
		try:

			if self.server is None:
				threading.Timer(1, self.open_browser).start()  # Wait a second before opening the browser
			#self.app.run(host='0.0.0.0', port=5000)
			self.server = make_server('0.0.0.0', 8888, self.app)#, request_handler = QuietRequestHandler)
			self.server.serve_forever()

			#from gevent.pywsgi import WSGIServer
			#from gevent import monkey
			#monkey.patch_all()
			#self.server = WSGIServer(('', 5000), self.app.wsgi_app)
			#self.server.serve_forever()

		except Exception as e:
			import traceback
			self.serverSignal.emit(traceback.format_exc())

	def updateCoords(self,c):
		self.coords = c
		#print(c)

	def stop_flask_app(self):
		if hasattr(self, 'server') and self.server:
			self.server.shutdown()

		self.delMPSignal.emit()
		# Perform any necessary cleanup before stopping the app
		# Stop the Flask app

	def construct_mp_blueprint(self):
		myblueprint = Blueprint('mp_blueprint', __name__)
		@myblueprint.route('/addMP', methods=['GET'])
		def addMP():
			loop = QEventLoop()
			# Slot to handle the ready signal
			def on_camera_ready():
				loop.quit()  # Stop the event loop once signal is received

			self.cameraReadySignal.connect(on_camera_ready)
			self.addMPSignal.emit()
			print('connected camera ready signal...waiting..')
			loop.exec_()
			print('camera is ready. responding.')

			return jsonify({'response': 'ready'})

		@myblueprint.route('/delMP', methods=['GET'])
		def delMP():
			self.delMPSignal.emit()
			return jsonify({'response': 'closed camera'})

		@myblueprint.route('/isHandVisible', methods=['GET'])
		def isHandVisible():
			self.queryMPSignal.emit()
			return jsonify({'response': True if self.coords is not None else False})

		@myblueprint.route('/getMPDistance', methods=['POST'])
		def getMPDistance():
			self.queryMPSignal.emit()
			data = request.json
			p1 = data['p1']
			p2 = data['p2']
			if p1<len(self.coords) and p2 < len(self.coords):
				c1 = self.coords[p1]
				c2 = self.coords[p2]
				return jsonify({'distance': np.sqrt( (c2[0]-c1[0])**2 + (c2[1]-c1[1])**2 )})
			else:
				return jsonify({'distance': 0})


		return(myblueprint)