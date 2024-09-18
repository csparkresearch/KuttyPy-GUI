from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

# blueprint for socket comms parts of app
flask_thread = None
showStatusSignal = None
import socket, threading


def setStatusSignal(sig):
    global showStatusSignal
    showStatusSignal = sig


def create_server(showStatusSignal, serverSignal, removeSignal, imageSignal, local_ip):
    setStatusSignal(showStatusSignal)
    mythread = QuizResponseThread()
    mythread.setServerSignal(serverSignal)
    mythread.setRemoveSignal(removeSignal)
    mythread.setImageSignal(imageSignal)
    # flask_thread.finished.connect(QApplication.quit)
    # Start the thread
    mythread.start()
    return mythread


connections = {}


class QuizResponseThread(QThread):
    finished = pyqtSignal()
    serverSignal = None
    removeSignal = None
    imageSignal = None

    def setServerSignal(self, sig):
        self.serverSignal = sig

    def setRemoveSignal(self, sig):
        self.removeSignal = sig

    def setImageSignal(self, sig):
        self.imageSignal = sig

    def run(self):
        try:
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serversocket.bind(('0.0.0.0', 4000))
            self.serversocket.listen(100)  # become a server socket, maximum 50 connections
            while True:
                connection, address = self.serversocket.accept()
                if address in connections:
                    print('player was already here!')
                    #connections[address].shutdown()
                addr = address[0]
                print(f"[*] Accepted connection from {address[0]}:{address[1]}:{addr}")

                connections[addr] = connection
                self.serverSignal.emit(address[0], 'RESP?:\t---')

                client_thread = threading.Thread(target=handle_client,
                                                 args=(connection, address, self.serverSignal, self.removeSignal,
                                                       self.imageSignal))
                client_thread.start()

                '''
                connection, address = self.serversocket.accept()
                buf = connection.recv(64)
                if len(buf) > 0:
                    print(address, buf)
                    self.serverSignal.emit(str(address[0]), buf.decode('utf-8'))
                '''
        except Exception as e:
            print(e)


def handle_client(client_socket, addr, serverSignal, removeSignal, imageSignal):
    #print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
    #serverSignal.emit(str(addr[0]), '?:%s\t0/0' % (addr[0]))
    buf = b''
    while True:
        try:
            buf = client_socket.recv(1024)
            if len(buf) > 0:
                print('handle_client', addr, buf)
                if buf[:4] == b'SCR\n':  #Screenshot
                    if len(buf) >= 8:
                        print(buf)
                        size = int.from_bytes(buf[4:8], 'big')
                        print("Image size:", size)
                        # Receive image data
                        image_data = buf[8:]
                        while len(image_data) < size:
                            chunk = client_socket.recv(size - len(image_data))
                            if not chunk:
                                return None
                            image_data += chunk
                        imageSignal.emit(image_data)
                        buf=b''
                else:  # Quiz Response
                    print('quiz resp', type(addr[0]))
                    serverSignal.emit(addr[0], buf[4:].decode('utf-8'))
                    buf = b''
            else:
                print('bye', addr)
        except socket.error:
            removeSignal.emit(addr[0])
            if addr[0] in connections:
                connections.pop(addr[0])
                return

        try:
            if not buf and addr[0] in connections:
                removeSignal.emit(addr[0])
                client_socket.close()
                connections.pop(addr[0])
                print(f"[*] Connection from {addr[0]}:{addr[1]} closed")
                removeSignal.emit(addr[0])
                return
        except Exception as e:
            print(e)
            removeSignal.emit(addr)
            return
