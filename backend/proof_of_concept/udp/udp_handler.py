from threading import Thread
from udp.udp_listener import UdpListener


class UdpHandler:

    # static variables
    listener: UdpListener = None
    # / static variables

    def __init__(self):
        pass

    def udp_test(self):
        UdpHandler.listner = UdpListener("127.0.0.1", 20777)
        Thread(target=UdpHandler.listner.start_listen, daemon=True).start()
        print(f"listening started on {UdpHandler.listner.ip}:{UdpHandler.listner.port}")

    def get_data(self):
        return UdpHandler.listner.data
