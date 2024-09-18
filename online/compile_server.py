import typing

from flask import Flask, request
from flask_cors import CORS
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

# blueprint for socket comms parts of app
from .compile_routes import main as main_blueprint, local_ip
from .compile_routes import setStatusSignal, setKpyPath
from .blockly_routes import bly as blockly_blueprint
from .blockly_routes import setBlocklyPath, setP
from werkzeug.serving import make_server
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


class FlaskThread(QThread):
	finished = pyqtSignal()
	serverSignal = None

	def __init__(self, parent=None):
		super().__init__(parent)
		self.server = None

	def setServerSignal(self, sig):
		self.serverSignal = sig

	def open_browser(self):
		state = 'false'
		if device is not None:
			if device.connected:
				state = 'true'

		if len(server_ip)>0:
			webbrowser.open(f"http://{server_ip}:5000/visual" + '?connected='+state)  # Adjust the URL as needed
		else:
			webbrowser.open(f"http://localhost:5000/visual"+ '?connected='+state)  # Adjust the URL as needed

	def run(self):
		# Run the Flask app in a separate thread
		print('starting the flask app...')
		self.app = Flask(__name__, template_folder='flask_templates', static_folder='static', static_url_path='/')
		CORS(self.app)
		self.app.register_blueprint(main_blueprint)
		self.app.register_blueprint(blockly_blueprint)
		try:

			if self.server is None:
				threading.Timer(1, self.open_browser).start()  # Wait a second before opening the browser
			#self.app.run(host='0.0.0.0', port=5000)
			self.server = make_server('0.0.0.0', 5000, self.app)
			self.server.serve_forever()

			#from gevent.pywsgi import WSGIServer
			#from gevent import monkey
			#monkey.patch_all()
			#self.server = WSGIServer(('', 5000), self.app.wsgi_app)
			#self.server.serve_forever()

		except Exception as e:
			import traceback
			self.serverSignal.emit(traceback.format_exc())

	def stop_flask_app(self):
		if hasattr(self, 'server') and self.server:
			self.server.shutdown()
			# Perform any necessary cleanup before stopping the app
			# Stop the Flask app