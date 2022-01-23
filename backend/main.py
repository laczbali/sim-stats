from classes.base.AppSettings import AppSettings
from classes.base.UdpHandler import UdpHandler
from classes.game.GameDirtRally2 import GameDirtRally2


def main():

    gh = GameDirtRally2()
    gh.start_listening()
    gh.start_run()


if __name__ == "__main__":
    main()
