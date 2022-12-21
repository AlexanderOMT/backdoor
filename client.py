

import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.43.88', 4444))
    s.sendall(b"Hi, this is a test server")

    while 1:
        data = s.recv(1024)
        if not data:
            break
        print('Received: ', data)
        s.send(data)

#print(f"Received {data!r}")
