from threading import Thread
from udp.udp_listener import OldUdpListener


class OldUdpHandler:

    # static variables
    listener: OldUdpListener = None
    # / static variables

    def __init__(self):
        pass

    def udp_test(self):
        OldUdpHandler.listner = OldUdpListener("127.0.0.1", 20777)
        Thread(target=OldUdpHandler.listner.start_listen, daemon=True).start()
        print(f"listening started on {OldUdpHandler.listner.ip}:{OldUdpHandler.listner.port}")

    def get_data(self):
        return OldUdpHandler.listner.data
