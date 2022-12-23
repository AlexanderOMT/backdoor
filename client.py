

import socket, sys

ip = '192.168.1.147'

while True:    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, 4444))
            sys.stdout.write(f'\r[*] Connected to {ip} ...')
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

#print(f"Received {data!r}")
