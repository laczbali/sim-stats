from classes.base.AppSettings import AppSettings
from classes.base.UdpHandler import UdpHandler

def main():
    udp = UdpHandler()
    udp.start_listen(20777)

    while True:
        in1 = input("Command: ")

        if in1 == "exit":
            break
        elif in1 == "read":
            print(udp.get_data())
        elif in1 == "start":
            udp.start_listen(20777)
        elif in1 == "stop":
            udp.stop_listen()


if __name__ == "__main__":
    main()
