#!/usr/bin/env python

import socket
import multiprocessing
import threading
import sys
from threading import Event
from threading import Thread
import queue
import time
import input_output

class Server:
    def __init__(self, host, port):
        self.host, self.port = host, port

        self.EXIT_COMMAND = 'exit server'
        self.REBOOT_COMMAND = 'reboot server'
        self.EMPTY_BYTE = b''
        self.thread_read_name = 'read_thread'
        self.thread_write_name = 'write_thread'
        self.time_out = 3.0

        self.cli_queue = queue.Queue()
        self.buffer = str()
        self.threads = list()
        self.handle_io_lock = threading.Lock()

        self.standard_stream = input_output.CustomStandardStream(
            thread_read_name = self.thread_read_name,
            thread_write_name = self.thread_write_name,
        )

    def manage_flag(self):
        # TODO refractor
        if self.buffer == self.EXIT_COMMAND:
            return True
        if self.buffer == self.REBOOT_COMMAND:
            return True
        if self.buffer == self.EMPTY_BYTE:
            return True
        return False
    
    def _read_client(self, client_socket):
        client_socket.settimeout( self.time_out )
        while True:
            try:
                read = client_socket.recv(1024)
                assert read != self.EMPTY_BYTE, ConnectionError()
                read = read.decode()

                self.handle_io_lock.acquire()
                self.standard_stream.handle_io(thread_name=threading.current_thread().name, notify=read)
                self.handle_io_lock.release()

            except socket.timeout:
                pass
            except AssertionError as e:
                sys.stdout.write(f'\r[-] Connection broken, likely from client side. Rebooting Server...')
                self.cli_queue.put(self.REBOOT_COMMAND)
                break
            except Exception:
                pass

            if self.manage_flag():
                client_socket.close()
                break

    def _write_client(self, client_socket):

        while True:

            self.handle_io_lock.acquire()
            read_out = self.standard_stream.handle_io(thread_name=threading.current_thread().name, notify=client_socket.getpeername())                   
            self.handle_io_lock.release()

            self.cli_queue.put(read_out)
    
            if self.cli_queue.qsize() > 0:   
                self.buffer = self.cli_queue.get()
                if self.manage_flag():
                    client_socket.close()
                    break
                client_socket.sendall(bytes(self.buffer, encoding='utf8'))
                

    def start(self):
        wait_threads = lambda list_thread: [thread.join() for thread in list_thread]
        while self.buffer != self.EXIT_COMMAND:

            self.server = socket.create_server(
                (self.host, self.port), reuse_port=True,
            )

            print(f'[+] Server {self.server.getsockname()} listening...')
            client_socket, client_addr = self.server.accept()
            print(f'[+] Connected to {client_socket.getpeername()} ')

            read_thread = threading.Thread(
                target = self._read_client, args = (client_socket,), 
                name = self.thread_read_name,
                daemon=False, )
            write_thread = threading.Thread(
                target = self._write_client, args = (client_socket,), 
                name = self.thread_write_name,
                daemon=False, )

            self.threads.append(read_thread)
            self.threads.append(write_thread)
            
            read_thread.start()
            write_thread.start()
       
            wait_threads(self.threads)

            if self.buffer == self.REBOOT_COMMAND:
                self._stop_threads()
                self.close_server()

        self.close_server()

    def _stop_threads(self):
        print(f'[+] Stopping threads...')
        for thread in self.threads:            
            if (thread.is_alive()):
                time.sleep( self.time_out )    
            print(f'[?] {thread.name} {type(thread)} alive: {thread.is_alive()}')

    def close_server(self):
        self.server.close()
        self._stop_threads()
        self.cli_queue.queue.clear()
        self.buffer = None
        print(f'[+] Server closed succesfully...')
    
server = Server('192.168.1.147', 4444)

try:
    server.start()
except Exception as e:
    server.close_server()
    exit(-1)
exit(0)
