import socket

class UdpListener:


    ip = None
    port = None
    data = None


    def __init__(self, ip, port):
        """
        Constructor sets up the socket
        @param ip: IP address to listen on (string)
        @param port: Port to listen on (int)
        """
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, # Internet
                                  socket.SOCK_DGRAM) # UDP
        self.sock.bind((self.ip, self.port))


    def start_listen(self):
        """
        Start listening, stores data in self.data
        """
        while True:
            self.data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes