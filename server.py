import socket
import multiprocessing
import threading
import sys
from threading import Event
from stoppable_thread import StoppableThread
import queue

class Server:
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.EXIT_COMMAND = 'exit'
        self.threads = list()
        self.server = socket.socket()
        self.server.bind( (host, port) )
    
    def _handle_io(self, reading, read = None, write = None):
        sys.stdout.write('\x1b[2K')
        if not reading:
            sys.stdout.write(f'\r[*] {self.host}:{self.port} >> {write}')
            pass
        else:
            sys.stdout.write(f'\r[+] Server read: {read} \n')

    def read_cli(self, stop_threads, cli_queue):
        # TODO this function shouldnt be here   
        while True:
            read_out = input()
            cli_queue.put(read_out)
            if stop_threads():
                break

    def _read_client(self, stop_threads, client_socket):
        while True:
            read = client_socket.recv(1024)
            if read:
                self._handle_io(reading=True, read=read)
            if stop_threads():
                break

    def _write_client(self, stop_threads, client_socket):
        cli_queue = queue.Queue()

        read_cli_thread = threading.Thread(target = self.read_cli, args=(stop_threads, cli_queue,))
        self.threads.append(read_cli_thread)
        read_cli_thread.start()

        while True:
            self._handle_io(reading=False)
            if cli_queue.qsize() > 0:

                command = cli_queue.get()
                if command == self.EXIT_COMMAND:
                    break
                client_socket.sendall(bytes(command, encoding='utf8'))
                

    def start(self):
        self.server.listen()

        print(f'[+] Server [{self.host}:{self.port}] listening...')

        client_socket, client_addr = self.server.accept()

        stop_threads = False

        # TODO multithreading or multiprocessing ?
        read_thread = threading.Thread(
            target = self._read_client, args = (lambda: stop_threads, client_socket,))
        write_thread = threading.Thread(
            target = self._write_client, args = (lambda: stop_threads, client_socket,))

        self.threads.append(read_thread)
        read_thread.start()
        self.threads.append(write_thread)
        write_thread.start()

        write_thread.join()
        #read_thread.join()
        stop_threads = True

    def _force_stop_threads(self):
        print()
        for thread in self.threads:
            # TODO stop them
            print(f'{thread.name} alive: {thread.is_alive()}')
            """
            if (thread.is_alive()):
                thread._stop_event.set()
            """
            print(f'{thread.name} alive: {thread.is_alive()}')
    def stop(self):
        self.server.close()
        self._force_stop_threads()
        print(f'[+] Server stopped succesfully...')
    
server = Server('192.168.43.88', 4444)

try:
    server.start()
except Exception:
    pass
server.stop()
exit(0)
