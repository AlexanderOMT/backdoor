import threading
from threading import Event

class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._stop_thread = threading.Event()

    def stop(self):
        self._stop_thread.set()

    def is_stopped(self):
        return self._stop_thread.is_set()
    