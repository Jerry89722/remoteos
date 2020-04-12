import os
import socket

from utils.socketmanager.socketmanager import SocketManager


from remoteos.settings import VLC_SOCK_PATH, VLC_CACHE_PATH, VLC_SOCK_FILE

from pyinotify import WatchManager, Notifier, ProcessEvent
import pyinotify


class EventHandler(ProcessEvent):
    """事件处理"""
    def __init__(self, unix_sock_man):
        super().__init__()
        self.unix_sock_man = unix_sock_man

    def process_IN_CREATE(self, event):
        print("Create operation: %s " % os.path.join(event.path, event.name))
        if event.name == VLC_SOCK_FILE:
            self.unix_sock_man.disconnect()
            self.unix_sock_man.connect()

    def process_IN_DELETE(self, event):
        print("delete operation: %s " % os.path.join(event.path, event.name))
        self.unix_sock_man.disconnect()


class UnixSocketManager(SocketManager):
    def socket_init(self):
        self.connect()

    def socket_loop(self):
        wm = WatchManager()
        mask = pyinotify.IN_CREATE | pyinotify.IN_DELETE
        notifier = Notifier(wm, EventHandler(self))
        wm.add_watch(VLC_CACHE_PATH, mask, rec=True)

        while True:
            try:
                notifier.process_events()
                if notifier.check_events():
                    notifier.read_events()
            except KeyboardInterrupt:
                notifier.stop()
                break

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(VLC_SOCK_PATH)
            print("socket connect ok")
        except socket.error as msg:
            print("unix socket connect failed", msg)


if __name__ == '__main__':
    usm = UnixSocketManager()

