import math
import time

from classes.game.RunData import RunData
from classes.game.GameHandler import GameHandlerState
from classes.base.AppSettings import AppSettings
from classes.base.UdpHandler import UdpHandler
from classes.game.GameDirtRally2 import GameDirtRally2


def main():

    gh = GameDirtRally2()
    gh.start_run()

    while not gh.is_run_over():
        pass

    print(
        "* run Over: "
        + gh.get_state().name
        + " in "
        + RunData.format_time(gh.get_run_result().run_time_sec)
    )


if __name__ == "__main__":
    main()
