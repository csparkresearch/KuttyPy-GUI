from PyQt5.QtCore import QThread, pyqtSignal
import socketio, threading
from PyQt5.QtWidgets import QApplication
from aiohttp import web
import asyncio

# blueprint for socket comms parts of app
socketio_server = None
import socket

connections = {}

class SocketIOClient:
    finished = pyqtSignal()
    showStatusSignal = pyqtSignal()
    memberSignal = pyqtSignal()
    serverSignal = None
    removeSignal = None
    imageSignal = None

    def __init__(self, showstatsig, serversig,removesig,  imagesig, memSig, roomparams, url,local_ip):
        # Create a Socket.IO client instance
        self.sio = socketio.Client()

        # Define the server URL
        self.server_url = url

        # Register event handlers
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('response', self.on_response)

        self.sio.on('quiz_created', self.on_quiz_created)
        self.sio.on('create_error', self.on_create_error)
        self.sio.on('member_list', self.on_member_list)
        self.sio.on('response', self.on_response)

        # Define host and port
        self.host = url
        self.roomparams = roomparams
        self.teacher_name = roomparams[0]
        self.room_name = roomparams[1]
        self.room_pass = roomparams[2]
        self.local_ip = local_ip
        self.showStatusSignal = showstatsig
        self.serverSignal = serversig
        self.removeSignal = removesig
        self.imageSignal = imagesig
        self.memberSignal = memSig



    # Start the client in a separate thread
    def start_client(self):
        # Create and start a thread for the client
        self.client_thread = threading.Thread(target=self.run)
        self.client_thread.daemon = True
        self.client_thread.start()

    # Method to run the client
    def run(self):
        # Connect to the server
        self.sio.connect(self.server_url)

        # Wait indefinitely (Socket.IO handles reconnections automatically)
        self.sio.wait()

    # Event handler for connect
    def on_connect(self):
        print("Client connected to the server")
        # Optionally send a message to the server after connecting
        self.sio.emit('create_quiz', {'owner_name':self.teacher_name, 'room_id': self.room_name, 'password': self.room_pass})
        self.sio.emit('message', {'data': 'Hello, Server!'})
        self.showStatusSignal.emit('connected to server', False)

    # Event handler for disconnect
    def on_disconnect(self):
        print("Client disconnected from the server")
        self.showStatusSignal.emit('Connection lost', True)

    # Event handler for messages from the server
    def on_response(self, data):
        #print(f"Received response from server: {data}")
        #self.showStatusSignal.emit(str(data), False)
        name = data.get('name')
        sid = data.get('sid')
        response= data.get('response')

        #print('handle_client', name, response[:10])
        if response[:4] == b'ABCD':  #Screenshot
            getting_screenshot = True
            print(response)
            size = int.from_bytes(response[4:8], 'big')
            print("Image size:", size)
            # Receive image data
            image_data = response[8:]
            self.imageSignal.emit(name,image_data)
        else:  # Quiz Response
            print('quiz resp', response)
            self.serverSignal.emit(name, response)




    def on_quiz_created(self,data):
        print(f"Quiz created: {data['room_id']}")
        self.showStatusSignal.emit(f"Room created: {data['room_id']}", False)

    def on_create_error(self, data):
        print(f"Room creation failed: {data}")
        self.showStatusSignal.emit(f"Room creation failed: {data}", True)

    def on_member_list(self,data):
        print(f"latest members: {data}")
        self.showStatusSignal.emit(f"members: {data.get('members','')}", False)
        self.memberSignal.emit(data.get('members',''))

    # Send a message to the server
    def send_message(self, message):
        self.sio.emit('message', {'data': message})
    # Send questions to room

    def dispatch(self, questions):
        self.sio.emit('send_question_batch', {'room_id': self.room_name,'data':questions})

    # Stop the client thread (optional)
    def stop_client(self):
        self.sio.disconnect()