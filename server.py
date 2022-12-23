import socket
import multiprocessing
import threading
import sys
from threading import Event

import queue
import time

class Server:
    def __init__(self, host, port):
        self.host, self.port = host, port
        self.EXIT_COMMAND = 'exit'
        self.time_out = 1.0
        self.buffer = str()
        self.threads = list()
        self.handle_io_lock = threading.Lock()
        self.server = socket.create_server(
            (host, port),
        )
    
    def _handle_io(self, reading, write = None, read = None):

        sys.stdout.write('\x1b[2K') # clear cursor line
        if not reading:
            sys.stdout.write(f'\r[*] {self.host}:{self.port} >> ')
            return input() 
        else:
            sys.stdout.write(f'\r[+] Server read: {read} \n')
    
    def _read_client(self, client_socket):
        client_socket.settimeout(self.time_out)
        while True:
            try:
                read = client_socket.recv(4096)
                self.handle_io_lock.acquire()
                self._handle_io(reading=True, read=read)
                self.handle_io_lock.release()
            except socket.timeout:
                pass

            if self.buffer == self.EXIT_COMMAND:
                    break

    def _write_client(self, client_socket):

        cli_queue = queue.Queue()

        while True:

            self.handle_io_lock.acquire()
            read_out = self._handle_io(reading=False)                   
            self.handle_io_lock.release()

            cli_queue.put(read_out)
    
            if cli_queue.qsize() > 0:   
                self.buffer = cli_queue.get()
                if self.buffer == self.EXIT_COMMAND:
                    break
                client_socket.sendall(bytes(self.buffer, encoding='utf8'))
                

    def start(self):
        self.server.listen()

        print(f'[+] Server [{self.host}:{self.port}] listening...')
        client_socket, client_addr = self.server.accept()
        print(f'[+] Connected to [{client_addr[0]}:{client_addr[1]}] ^-^ ')

        read_thread = threading.Thread(
            target = self._read_client, args = (client_socket,))
        write_thread = threading.Thread(
            target = self._write_client, args = (client_socket,))

        self.threads.append(read_thread)
        read_thread.start()
        self.threads.append(write_thread)
        write_thread.start()

        write_thread.join()
        read_thread.join()
        

    def _force_stop_threads(self):
        print(f'[+] Stop threads...')
        for thread in self.threads:            
            if (thread.is_alive()):
                time.sleep(self.time_out)      
            print(f'{thread.name} {type(thread)} alive: {thread.is_alive()}')
    def stop(self):
        self.server.close()
        self._force_stop_threads()
        print(f'[+] Server stopped succesfully...')
    
server = Server('192.168.1.147', 4444)

try:
    server.start()
except Exception:
    print(f'[-] Server closed with exception')
server.stop()
exit(0)
