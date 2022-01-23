from threading import Thread
import socket


class UdpHandler:
    """
    A static class, that listens for incoming UDP packets in a daemon thread.

    - The thread is started by calling start_listen(port, buffer_size)
    - The thread is stopped by calling stop_listen().
    - The data from the last UDP packet received is returned by calling get_data().
    """

    # class (static) variables
    _listener_thread: Thread = None
    _stop_thread: bool = False
    _data: bytes = None



    def __init__(self) -> None:
        pass



    def start_listen(self, port: int, buffer_size: int = 1024) -> None:
        """
        Starts listening on the specified port.
        Closes previous conenction if one exists.
        """

        # close previous connection if one exists
        if UdpHandler._listener_thread is not None:
            while UdpHandler._listener_thread.is_alive():
                UdpHandler._stop_thread = True
        UdpHandler._stop_thread = False

        # start new listener thread
        UdpHandler._listener_thread = Thread(
            target=UdpHandler._listen, daemon=True, args=(port, buffer_size)
        )
        UdpHandler._listener_thread.start()



    def stop_listen(self) -> None:
        """
        Stops listening.
        """
        UdpHandler._stop_thread = True



    def get_data(self) -> bytes:
        """
        Returns data from the last UDP packet received.
        """
        return UdpHandler._data



    def _listen(port, buffer_size) -> None:
        """
        Listens for incoming UDP packets.
        Stores data in UdpHandler.data
        """

        # set up UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet, UDP
        sock.bind(("127.0.0.1", port))
        sock.settimeout(0.1)

        # listen for incoming UDP packets until stop_thread is set to True
        while not UdpHandler._stop_thread:
            try:
                UdpHandler._data, addr = sock.recvfrom(buffer_size)
            except socket.timeout:
                pass
