from flask import Flask, request
from flask_cors import CORS
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

# blueprint for socket comms parts of app
from .compile_routes import main as main_blueprint
from .compile_routes import setStatusSignal, setKpyPath
from werkzeug.serving import make_server
print('starting the compile server...')

flask_thread = None


def create_server(showStatusSignal, serverSignal, kpy_path, local_ip):
	setStatusSignal(showStatusSignal)
	setKpyPath(kpy_path, local_ip)
	flask_thread = FlaskThread()
	flask_thread.setServerSignal(serverSignal)
	# flask_thread.finished.connect(QApplication.quit)

	# Start the thread
	flask_thread.start()
	return flask_thread


class FlaskThread(QThread):
	finished = pyqtSignal()
	serverSignal = None

	def setServerSignal(self, sig):
		self.serverSignal = sig

	def run(self):
		# Run the Flask app in a separate thread
		print('starting the flask app...')
		self.app = Flask(__name__, template_folder='compile_templates')
		CORS(self.app)
		self.app.register_blueprint(main_blueprint)
		try:
			#self.app.run(host='0.0.0.0', port=5000)
			self.server = make_server('0.0.0.0', 5000, self.app)
			self.server.serve_forever()
		except Exception as e:
			import traceback
			self.serverSignal.emit(traceback.format_exc())

	def stop_flask_app(self):
		if hasattr(self, 'server') and self.server:
			self.server.shutdown()
			# Perform any necessary cleanup before stopping the app
			# Stop the Flask app