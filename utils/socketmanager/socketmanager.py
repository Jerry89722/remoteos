import threading
import socket
from abc import abstractmethod


class SocketManager:
    def __init__(self):
        self.sock = None

        self.socket_init()

        self.__lock = threading.Lock()
        self.__t_sock_loop = threading.Thread(target=self.socket_loop)
        self.__t_sock_loop.start()

    def __del__(self):
        self.disconnect()

    @abstractmethod
    def connect(self):
        pass

    def disconnect(self):
        if self.sock is None:
            return
        self.sock.close()
        self.sock = None

    def recv(self, rlen: int):
        return self.sock.recv(rlen)

    def sendall(self, data):
        self.sock.sendall(data)

    @abstractmethod
    def socket_loop(self):
        pass

    def lock(self):
        pass

    def unlock(self):
        pass

    @abstractmethod
    def socket_init(self):
        print("abstractmethod: socket init")



