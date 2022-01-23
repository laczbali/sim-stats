from enum import Enum
import struct
from threading import Thread
import math

from classes.game.RunData import RunData
from classes.game.GameHandler import GameHandler, GameHandlerState


class GameDirtRally2(GameHandler):

    def _bit_stream_to_float32(data, pos):
        try:
            return struct.unpack("f", data[pos : pos + 4])[0]
        except Exception as e:
            return 0

    # -----------------------------------------------------------------------------------------------------------------
    # Parent class abstract methods
    # -----------------------------------------------------------------------------------------------------------------

    def parse_udp_data(self) -> RunData:
        """
        Parses the latest UDP packet received, returns it in the generalized format
        """

        lap_time = GameDirtRally2._bit_stream_to_float32(
            self.udp_data(), DirtRally2Fields.lap_time.value * 4
        )
        last_lap_time = GameDirtRally2._bit_stream_to_float32(
            self.udp_data(), DirtRally2Fields.last_lap_time.value * 4
        )

        run_data = RunData()
        run_data.run_time_sec = lap_time
        run_data.last_lap_time_sec = last_lap_time

        return run_data



    def start_run(self):
        """
        - Sets the state to WAITING_FOR_START
        - Starts a new thread to parse incoming UDP data
        - Once it detected the run has started, it will set the state to RUNNING
        - At this point the current RunData can be queried with get_run_progress()
        - Once the run finish is detected, the state will be set to FINISHED
        - At this point the run needs to be processed (edited/saved/discarded) with process_run()
        - That will set the state back to IDLE, and the next run can be started (with start_run())
        """

        # Start parsing the incoming UDP data
        print("starting run")
        self._set_state(GameHandlerState.WAITING_FOR_START)
        Thread(target=self._gather_data, daemon=True).start()

        while self.get_state() != GameHandlerState.FINISHED:
            pass

        runtime_sec = self.run_result.last_lap_time_sec
        print(
            "{:02.0f}:{:02.0f}:{:03.0f}".format(
                runtime_sec // 60, math.floor(runtime_sec % 60), (runtime_sec % 1) * 1000
            )
        )



    def _gather_data(self):
        last_runtime_value = 0
        current_runtime_value = 0
        data = None
        finished = False

        while not finished:
            data = self.parse_udp_data()

            # Change state based on current and last-iteration runtime values
            last_runtime_value = current_runtime_value
            current_runtime_value = data.run_time_sec

            # print(last_runtime_value, current_runtime_value)

            if last_runtime_value == 0 and current_runtime_value != 0:
                self._set_state(GameHandlerState.RUNNING)

            if last_runtime_value != 0 and current_runtime_value == 0:
                self.run_result = data
                self._set_state(GameHandlerState.FINISHED)
                finished = True        



    def get_run_progress(self):
        pass



    # def get_run_results(self):
    #     pass



    def process_run(self):
        pass



class DirtRally2Fields(Enum):
    """
    Dirt Rally 2 returns XX bytes of data per packet, arranged in a struct. Each field consists of 4 bytes, representing a float. The position of each field in the struct is specified in the following table.

    To set the game up, open C:\\Users\\USERNAME\\Documents\\My Games\\DiRT Rally 2.0\\hardwaresettings\\hardware_settings_config.xml and set up the following:
    - <udp enabled="true" extradata="3" ip="127.0.0.1" port="51659" delay="1" />

    Special thanks to https://github.com/ErlerPhilipp/dr2_logger for the struct format.
    """

    run_time = 0
    lap_time = 1
    distance = 2
    progress = 3
    pos_x = 4
    pos_y = 5
    pos_z = 6
    speed_ms = 7
    vel_x = 8
    vel_y = 9
    vel_z = 10
    roll_x = 11
    roll_y = 12
    roll_z = 13
    pitch_x = 14
    pitch_y = 15
    pitch_z = 16
    susp_rl = 17
    susp_rr = 18
    susp_fl = 19
    susp_fr = 20
    susp_vel_rl = 21
    susp_vel_rr = 22
    susp_vel_fl = 23
    susp_vel_fr = 24
    wsp_rl = 25
    wsp_rr = 26
    wsp_fl = 27
    wsp_fr = 28
    throttle = 29
    steering = 30
    brakes = 31
    clutch = 32
    gear = 33
    g_force_lat = 34
    g_force_lon = 35
    current_lap = 36
    rpm = 37  # / 10
    sli_pro_support = 38  # ignored
    car_pos = 39
    kers_level = 40  # ignored
    kers_max_level = 41  # ignored
    drs = 42  # ignored
    traction_control = 43  # ignored
    anti_lock_brakes = 44  # ignored
    fuel_in_tank = 45  # ignored
    fuel_capacity = 46  # ignored
    in_pit = 47  # ignored
    sector = 48
    sector_1_time = 49
    sector_2_time = 50
    brakes_temp_rl = 51
    brakes_temp_rr = 52
    brakes_temp_fl = 53
    brakes_temp_fr = 54
    tyre_pressure_rl = 55  # ignored
    tyre_pressure_rr = 56  # ignored
    tyre_pressure_fl = 57  # ignored
    tyre_pressure_fr = 58  # ignored
    laps_completed = 59
    total_laps = 60
    track_length = 61
    last_lap_time = 62
    max_rpm = 63  # / 10
    idle_rpm = 64  # / 10
    max_gears = 65
