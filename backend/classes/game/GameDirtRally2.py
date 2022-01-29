import datetime
from enum import Enum
import numpy as np
import struct
from threading import Thread
from collections import defaultdict

from classes.base.DBHandler import DBHandler
from classes.game.RunData import RunData
from classes.game.GameHandler import GameHandler, GameHandlerState


class GameDirtRally2(GameHandler):

    def __init__(self):
        super().__init__()
        
        self.car_list = DirtRally2CarList()
        self.track_list = DirtRally2TrackList()



    def _bit_stream_to_float32(data, pos):
        try:
            return struct.unpack("f", data[pos : pos + 4])[0]
        except Exception as e:
            return 0

    # -----------------------------------------------------------------------------------------------------------------
    # Parent class abstract methods
    # -----------------------------------------------------------------------------------------------------------------

    # abstractmethod
    def parse_udp_data(self):
        """
        Parses the latest UDP packet received, stores it in the generalized format in self._run_result
        """

        # if a previous container exists use that, else create a new one
        if self._run_result is None:
            run_data = RunData()
        else:
            run_data = self._run_result
        
        # lap times are not relevant for Dirt Rally 2
        # however the lap_time field contains the actual value of the current run
        # and we use that to detect state changes
        if len(run_data.lap_times_sec) == 0:
            run_data.lap_times_sec.append(0)
        run_data.lap_times_sec[0] = GameDirtRally2._bit_stream_to_float32(
            self.udp_data(), DirtRally2Fields.lap_time.value * 4
        )

        # the "last_lap_time" fields gets a value after a run has ended
        # it contains the run time of the run that just ended
        # during the run it is 0
        run_data.run_time_sec = GameDirtRally2._bit_stream_to_float32(
            self.udp_data(), DirtRally2Fields.last_lap_time.value * 4
        )

        # will always be 1
        run_data.total_laps = GameDirtRally2._bit_stream_to_float32(
            self.udp_data(), DirtRally2Fields.total_laps.value * 4
        )

        # 0 during the run, 1 if the run has ended with a finish
        run_data.laps_completed = GameDirtRally2._bit_stream_to_float32(
            self.udp_data(), DirtRally2Fields.laps_completed.value * 4
        )

        # get car & track info only when the run is started
        # runtime is the total runtime, including waiting for the green light
        if GameDirtRally2._bit_stream_to_float32(self.udp_data(), DirtRally2Fields.run_time.value * 4) > 0:

            # get car info
            if run_data.car == '' or run_data.car == "AUTO-DETECT":
                car = self.car_list.indentify_car(
                    GameDirtRally2._bit_stream_to_float32(self.udp_data(), DirtRally2Fields.max_rpm.value * 4),
                    GameDirtRally2._bit_stream_to_float32(self.udp_data(), DirtRally2Fields.idle_rpm.value * 4),
                    GameDirtRally2._bit_stream_to_float32(self.udp_data(), DirtRally2Fields.max_gears.value * 4)
                )
                run_data.car = car[0]
                run_data.car_class = car[1]
                print("* identified car: " + run_data.car + " of class: " + run_data.car_class)

            # get track info
            if run_data.track == '' or run_data.track == "AUTO-DETECT":
                run_data.track = self.track_list.indentify_track(
                    GameDirtRally2._bit_stream_to_float32(self.udp_data(), DirtRally2Fields.track_length.value * 4),
                    GameDirtRally2._bit_stream_to_float32(self.udp_data(), DirtRally2Fields.pos_z.value * 4)
                )
                print("* identified track: " + run_data.track)


        self._run_result = run_data



    # abstractmethod
    def start_run(self, run_config = None):
        """
        - Sets the state to WAITING_FOR_START
        - Starts a new thread to parse incoming UDP data
        - Once it detected the run has started, it will set the state to RUNNING
        - At this point the current RunData can be queried with get_run_progress()
        - Once the run finish is detected, the state will be set to FINISHED
        - At this point the run needs to be processed (edited/saved/discarded) with process_run()
        - That will set the state back to IDLE, and the next run can be started (with start_run())
        """

        # Make sure we are in the idle state
        if self.get_state() != GameHandlerState.IDLE:
            raise Exception("Can't start a run when not in IDLE state. Current state: " + str(self.get_state()))

        # Set run settings, if provided
        self._run_result = run_config
        
        # Start parsing the incoming UDP data
        self._set_state(GameHandlerState.WAITING_FOR_START)
        Thread(target=self._gather_data, daemon=True).start()



    def _gather_data(self):
        """
        - Handles state changes between WAITING_FOR_START, RUNNING, FINISHED and ABORTED
        - Calls the parser for the UDP data, so it will be a generic RunData
        - Sets the parsed data as the _run_result
        - Starts/Stops the UDP listner
        """

        print("* starting run for DirtRally2")

        last_runtime_value = 0
        current_runtime_value = 0
        self._stop = False

        self._start_listening()

        while not self._stop:
            self.parse_udp_data()

            # Change state based on current and last-iteration runtime values
            last_runtime_value = current_runtime_value
            current_runtime_value = self._run_result.lap_times_sec[0]
            
            if last_runtime_value == 0 and current_runtime_value != 0:
                # Run started
                self._set_state(GameHandlerState.RUNNING)
                self._run_result.run_date = datetime.datetime.now()

            if last_runtime_value != 0 and current_runtime_value == 0:
                # Run ended
                self._stop = True

                # decide if finished or aborted
                if self._run_result.laps_completed == self._run_result.total_laps:
                    self._set_state(GameHandlerState.FINISHED)
                else:
                    self._set_state(GameHandlerState.ABORTED)

        # adjust data stucture, because the general structure expects the run result in the lap_times_sec array
        self._run_result.lap_times_sec = [self._run_result.run_time_sec]

        # shut down UDP listener
        self._stop_listening()
        result_time_str = RunData.format_time(self._run_result.run_time_sec)
        print(f"* stopping run for DirtRally2 ( {result_time_str} )")



    # abstractmethod
    def stop_run(self):
        """
        Stops the current run, sets state to ABORTED
        """
        self._stop = True
        self._set_state(GameHandlerState.ABORTED)



    # abstractmethod
    def get_attributes():
        return {
            "car": {
                "supports_car_detection": True,
                "saved_cars": DBHandler.get_saved_cars("DirtRally2"),
                "saved_car_classes": DBHandler.get_saved_car_classes("DirtRally2")
            },

            "track": {
                "supports_track_detection": True,
                "saved_tracks": DBHandler.get_saved_tracks("DirtRally2"),
                "saved_track_conditions": DBHandler.get_saved_track_conditions("DirtRally2")
            },

            "saved_tags": DBHandler.get_saved_tags("DirtRally2"),

            "additional_fields": []
        }



class DirtRally2Fields(Enum):
    """
    Dirt Rally 2 returns XX bytes of data per packet, arranged in a struct. Each field consists of 4 bytes, representing a float. The position of each field in the struct is specified in the following table.

    To set the game up, open C:\\Users\\USERNAME\\Documents\\My Games\\DiRT Rally 2.0\\hardwaresettings\\hardware_settings_config.xml and set up the following:
    - <udp enabled="true" extradata="3" ip="127.0.0.1" port="51659" delay="1" />

    Special thanks to https://github.com/ErlerPhilipp/dr2_logger & https://github.com/soong-construction/dirt-rally-time-recorder for the struct format.
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



class DirtRally2CarList:
    """
    Special thanks to https://github.com/ErlerPhilipp/dr2_logger for the implementation.
    """

    def __init__(self):
        car_data = [
            # Crosskarts
            [1598.547119140625, 161.26841735839844, 6.0, 'Speedcar Xtrem', 'Crosskarts'],

            # RX Super 1600S
            [994.8377075195312, 188.49555969238281, 6.0, 'Volkswagen Polo S1600', 'RX Super 1600S'],
            [968.6577758789062, 198.96754455566406, 6.0, 'Renault Clio RS S1600', 'RX Super 1600S'],
            [994.8377075195312, 198.96754455566406, 6.0, 'Opel Corsa Super 1600', 'RX Super 1600S'],

            # RX Group B
            [890.1179809570312, 167.55160522460938, 5.0, 'Lancia Delta S4 RX', 'RX Group B'],  # same as Peugeot 208 R2 and Lancia Delta S4
            [942.477783203125, 167.55160522460938, 5.0, 'Ford RS200 Evolution', 'RX Group B'],
            [837.758056640625, 209.43951416015625, 5.0, 'Peugeot 205 T16 Evo 2 RX', 'RX Group B'],  # same as non-rx
            [994.8377075195312, 115.19173431396484, 5.0, 'MG Metro 6R4 RX', 'RX Group B'],

            # RX2
            [837.758056640625, 167.55160522460938, 6.0, 'Ford Fiesta OMSE SuperCar Lites', 'RX2'],

            # RX Supercars
            [874.4099731445312, 209.43951416015625, 6.0, 'Volkswagen Polo R Supercar', 'RX Supercars'],  # same as Audi S1 EKS RX quattro
            [874.4099731445312, 209.43951416015625, 6.0, 'Audi S1 EKS RX Quattro', 'RX Supercars'],  # same as Volkswagen Polo R Supercar
            [837.758056640625, 178.02359008789062, 6.0, 'Peugeot 208 WRX', 'RX Supercars'],  # same as Renault Clio R.S. RX
            [816.81414794921875, 172.78759765625, 5.0, 'Renault Megane RS', 'RX Supercars'],
            [811.578125, 188.49555969238281, 6.0, 'Ford Fiesta RX (MK8)', 'RX Supercars'],
            [785.398193359375, 172.78759765625, 6.0, 'Ford Fiesta RX (MK7)', 'RX Supercars'],
            [774.92620849609375, 178.02359008789062, 6.0, 'Subaru WRX STI RX', 'RX Supercars'],  # same as Skoda Fabia Rally

            # RX Supercars 2019
            [837.758056640625, 178.02359008789062, 5.0, 'Renault Megane R.S. RX', 'RX Supercars 2019'],  # same as Subaru Impreza WRX STI NR4
            [837.758056640625, 178.02359008789062, 6.0, 'Peugeot 208 WRX', 'RX Supercars 2019'],  # same as Renault Clio R.S. RX
            [874.4099731445312, 209.43951416015625, 6.0, 'Audi S1 EKS RX Quattro', 'RX Supercars 2019'],  # same as Volkswagen Polo R Supercar
            [837.758056640625, 178.02359008789062, 6.0, 'Renault Clio R.S. RX', 'RX Supercars 2019'],  # same as Peugeot 208 WRX
            [837.758056640625, 188.49555969238281, 6.0, 'Ford Fiesta RXS Evo 5', 'RX Supercars 2019'],  # same as Ford Fiesta RX (Stard)
            [811.578125, 188.49555969238281, 6.0, 'Ford Fiesta RX (MK8)', 'RX Supercars 2019'],  # same as Ford Fiesta RX (MK8)
            [785.398193359375, 261.79940795898438, 6.0, 'Mini Cooper SX1', 'RX Supercars 2019'],
            [837.758056640625, 188.49555969238281, 6.0, 'Ford Fiesta RX (Stard)', 'RX Supercars 2019'],  # same as Ford Fiesta RXS Evo 5
            [785.398193359375, 178.02359008789062, 6.0, 'Seat Ibiza RX', 'RX Supercars 2019'],  # same as Ford Focus RS Rally 2001

            # H1 FWD
            [733.03826904296875, 83.77580261230469, 4.0, 'Mini Cooper S', 'H1 FWD'],
            [628.31854248046875, 104.71975708007812, 4.0, 'Citroen DS 21', 'H1 FWD'],
            [680.678466796875, 99.48377227783203, 4.0, 'Lancia Fulvia HF', 'H1 FWD'],

            # H2 FWD
            [785.398193359375, 94.24777984619141, 5.0, 'Volkswagen Golf GTI 16V', 'H2 FWD'],
            [733.03826904296875, 125.66371154785156, 5.0, 'Peugeot 205 GTI', 'H2 FWD'],

            # H2 RWD
            [994.8377075195312, 125.66371154785156, 5.0, 'Ford Escort Mk II', 'H2 RWD'],
            [837.758056640625, 167.55160522460938, 5.0, 'Renault Alpine A110 1600 S', 'H2 RWD'],
            [837.758056640625, 178.02359008789062, 5.0, 'Fiat 131 Abarth Rally', 'H2 RWD'],  # same as Renault Megane R.S. RX
            [942.477783203125, 157.07963562011719, 5.0, 'Opel Kadett C GT/E', 'H2 RWD'],

            # H3 RWD
            [932.005859375, 115.19173431396484, 6.0, 'BMW E30 Evo Rally', 'H3 RWD'],
            [785.398193359375, 136.13568115234375, 5.0, 'Opel Ascona 400', 'H3 RWD'],
            [890.1179809570312, 104.71975708007812, 5.0, 'Lancia Stratos', 'H3 RWD'],
            [837.758056640625, 151.84365844726562, 5.0, 'Renault 5 Turbo', 'H3 RWD'],
            [779.7432861328125, 80.42477416992188, 5.0, 'Datsun 240Z', 'H3 RWD'],
            [785.398193359375, 115.19173431396484, 5.0, 'Ford Sierra Cosworth RS500', 'H3 RWD'],

            # F2 Kit Car
            [1151.9173583984375, 198.96754455566406, 6.0, 'Peugeot 306 Maxi', 'F2 Kit Car'],
            [942.477783203125, 136.13568115234375, 6.0, 'Seat Ibiza Kit Car', 'F2 Kit Car'],
            [942.477783203125, 125.66371154785156, 6.0, 'Volkswagen Golf Kitcar', 'F2 Kit Car'],

            # Group B RWD
            [890.1179809570312, 125.66371154785156, 5.0, 'Lancia 037 Evo 2', 'Group B RWD'],
            [816.81414794921875, 146.607666015625, 5.0, 'Opel Manta 400', 'Group B RWD'],
            [968.6577758789062, 157.07963562011719, 5.0, 'BMW M1 Procar Rally', 'Group B RWD'],
            [837.758056640625, 136.13568115234375, 5.0, 'Porsche 911 SC RS', 'Group B RWD'],

            # Group B 4WD
            [942.477783203125, 136.13568115234375, 5.0, 'Audi Sport quattro S1 E2', 'Group B 4WD'],
            [837.758056640625, 209.43951416015625, 5.0, 'Peugeot 205 T16 Evo 2', 'Group B 4WD'],
            [890.1179809570312, 167.55160522460938, 5.0, 'Lancia Delta S4', 'Group B 4WD'],  # same as Peugeot 208 R2
            [942.477783203125, 125.66371154785156, 5.0, 'Ford RS200', 'Group B 4WD'],
            [994.8377075195312, 109.95574188232422, 5.0, 'MG Metro 6R4', 'Group B 4WD'],

            # R2
            [816.81414794921875, 157.07963562011719, 5.0, 'Ford Fiesta R2', 'R2'],
            [905.825927734375, 178.02359008789062, 5.0, 'Opel Adam R2', 'R2'],
            [890.1179809570312, 167.55160522460938, 5.0, 'Peugeot 208 R2', 'R2'],  # same as Lancia Delta S4

            # Group A
            [733.03826904296875, 146.607666015625, 6.0, 'Mitsubishi Lancer Evo VI', 'Group A'],  # same as BMW M2 Competition
            [733.03826904296875, 115.19173431396484, 6.0, 'Subaru Impreza 1995', 'Group A'],
            [785.398193359375, 104.71975708007812, 6.0, 'Lancia Delta HF Integrale', 'Group A'],
            [733.03826904296875, 146.607666015625, 7.0, 'Ford Escort RS Cosworth', 'Group A'],
            [791.1577758789062, 202.4232940673828, 6.0, 'Subaru Legacy RS', 'Group A'],

            # NR4/R4
            [837.758056640625, 178.02359008789062, 5.0, 'Subaru Impreza WRX STI NR4', 'NR4/R4'],
            [785.398193359375, 178.02359008789062, 5.0, 'Mitsubishi Lancer Evo X', 'NR4/R4'],  # same as Peugeot 208 T16

            # 2000cc 4WD
            [774.92620849609375, 188.49555969238281, 6.0, 'Citroen C4 Rally', '2000cc 4WD'],
            [774.92620849609375, 178.02359008789062, 6.0, 'Skoda Fabia Rally', '2000cc 4WD'],  # same as Subaru WRX STI RX
            [769.69024658203125, 186.92477416992188, 5.0, 'Ford Focus RS Rally 2007', '2000cc 4WD'],
            [785.398193359375, 219.91148376464844, 6.0, 'Subaru Impreza 2008', '2000cc 4WD'],
            [785.398193359375, 178.02359008789062, 6.0, 'Ford Focus RS Rally 2001', '2000cc 4WD'],  # same as Seat Ibiza RX
            [837.758056640625, 204.2035369873047, 6.0, 'Subaru Impreza 2001', '2000cc 4WD'],
            [680.678466796875, 157.0796356201172, 5.0, 'Peugeot 206 Rally', '2000cc 4WD'],
            [816.8141479492188, 207.34512329101562, 6.0, 'Subaru Impreza S4 Rally', '2000cc 4WD'],

            # R5
            [774.92620849609375, 188.49555969238281, 5.0, 'Ford Fiesta R5', 'R5'],
            [785.398193359375, 178.02359008789062, 5.0, 'Peugeot 208 T16', 'R5'],  # same as Mitsubishi Lancer Evolution X
            [837.758056640625, 219.91148376464844, 5.0, 'Mitsubishi Space Star R5', 'R5'],
            [774.92620849609375, 178.02359008789062, 5.0, 'Skoda Fabia R5', 'R5'],  # same as Volkswagen Polo GTI R5
            [774.92620849609375, 178.02359008789062, 5.0, 'Volkswagen Polo GTI R5', 'R5'],  # same as Skoda Fabia R5
            [743.51031494140625, 185.87757873535156, 5.0, 'Citroen C3 R5', 'R5'],
            [774.9262084960938, 183.2595672607422, 5.0, 'Ford Fiesta R5 MKII', 'R5'],

            # Rally GT
            [942.477783203125, 188.4955596923828, 6.0, 'Porsche 911 RGT Rally Spec', 'Rally GT'],
            [733.03826904296875, 146.607666015625, 6.0, 'BMW M2 Competition', 'Rally GT'],  # same as Mitsubishi Lancer Evo VI
            [759.21820068359375, 178.02359008789062, 6.0, 'Chevrolet Camaro GT4.R', 'Rally GT'],
            [733.03826904296875, 104.71975708007812, 6.0, 'Aston Martin V8 Vantage GT4', 'Rally GT'],
            [863.9380493164062, 146.607666015625, 6.0, 'Ford Mustang GT4 Ford RS200', 'Rally GT'],
        ]
        
        self.car_dict = dict()
        for d in car_data:
            self.car_dict[(d[0], d[1], d[2])] = [d[3], d[4]]
    
    def indentify_car(self, max_rpm, idle_rpm, max_gears):
        """
        Identify the car based on the RPM and gear info.

        Returns: [CAR_NAME, CAR_CLASS]
        """

        key = (max_rpm, idle_rpm, max_gears)
        
        if key in self.car_dict.keys():
            car = self.car_dict[key]
        else:
            car = ['Unknown', 'Unknown']

        return car



class DirtRally2TrackList:
    """
    Special thanks to https://github.com/ErlerPhilipp/dr2_logger for the implementation.
    """

    def __init__(self):
        track_data = [
            # Baumholder, Germany
            [5361.90966796875, -2668.4755859375,  'DE, Baumholder, Waldaufstieg'],
            [5882.1796875, -948.372314453125,     'DE, Baumholder, Waldabstieg'],
            [6121.8701171875, -718.9346923828125, 'DE, Baumholder, Kreuzungsring'],
            [5666.25, 539.2579345703125,          'DE, Baumholder, Kreuzungsring reverse'],
            [10699.9599609375, 814.2764892578125, 'DE, Baumholder, Ruschberg'],
            [5855.6796875, 513.0728759765625,     'DE, Baumholder, Verbundsring'],
            [5550.85009765625, 657.1261596679688, 'DE, Baumholder, Verbundsring reverse'],
            [5129.0400390625, 814.3093872070312,  'DE, Baumholder, Innerer Feld-Sprint'],
            [4937.85009765625, 656.46044921875,   'DE, Baumholder, Innerer Feld-Sprint reverse'],
            [11487.189453125, -2668.59033203125,  'DE, Baumholder, Oberstein'],
            [10805.23046875, 513.07177734375,     'DE, Baumholder, Hammerstein'],
            [11551.16015625, 539.3564453125,      'DE, Baumholder, Frauenberg'],

            # Monte Carlo, Monaco
            [10805.220703125, 1276.76611328125,    'MC, Monte Carlo, Route de Turini'],
            [10866.8603515625, -2344.705810546875, 'MC, Monte Carlo, Vallee descendante'],
            [4730.02001953125, 283.7648620605469,  'MC, Monte Carlo, Col de Turini - Sprint en descente'],
            [4729.5400390625, -197.3816375732422,  'MC, Monte Carlo, Col de Turini sprint en Montee'],
            [5175.91015625, -131.84573364257812,   'MC, Monte Carlo, Col de Turini - Descente'],
            [5175.91015625, -467.3677062988281,    'MC, Monte Carlo, Gordolon - Courte montee'],
            [4015.35986328125, -991.9784545898438, 'MC, Monte Carlo, Route de Turini (Descente)'],
            [3952.150146484375, 1276.780517578125, 'MC, Monte Carlo, Approche du Col de Turini - Montee'],
            [9831.4501953125, -467.483154296875,   'MC, Monte Carlo, Pra d\'Alart'],
            [9832.0205078125, 283.4727478027344,   'MC, Monte Carlo, Col de Turini Depart'],
            [6843.3203125, -991.945068359375,      'MC, Monte Carlo, Route de Turini (Montee)'],
            [6846.830078125, -2344.592529296875,   'MC, Monte Carlo, Col de Turini - Depart en descente'],

            # Powys, Wales
            [4821.64990234375, 2047.56201171875,   'UK, Powys, Pant Mawr Reverse'],
            [4960.06005859375, 1924.06884765625,   'UK, Powys, Bidno Moorland'],
            [5165.96044921875, 2481.105224609375,  'UK, Powys, Bidno Moorland Reverse'],
            [11435.5107421875, -557.0780029296875, 'UK, Powys, River Severn Valley'],
            [11435.5400390625, 169.15403747558594, 'UK, Powys, Bronfelen'],
            [5717.39990234375, -557.11328125,      'UK, Powys, Fferm Wynt'],
            [5717.3896484375, -22.597640991210938, 'UK, Powys, Fferm Wynt Reverse'],
            [5718.099609375, -23.46375274658203,   'UK, Powys, Dyffryn Afon'],
            [5718.10009765625, 169.0966033935547,  'UK, Powys, Dyffryn Afon Reverse'],
            [9911.66015625, 2220.982177734375,     'UK, Powys, Sweet Lamb'],
            [10063.6005859375, 2481.169677734375,  'UK, Powys, Geufron Forest'],
            [4788.669921875, 2221.004150390625,    'UK, Powys, Pant Mawr'],

            # Värmland, Sweden
            [7055.9501953125, -1618.4476318359375, 'SE, Värmland, Älgsjön'],
            [4911.68017578125, -1742.0498046875,   'SE, Värmland, Östra Hinnsjön'],
            [6666.89013671875, -2143.403076171875, 'SE, Värmland, Stor-jangen Sprint'],
            [6693.43994140625, 563.3468017578125,  'SE, Värmland, Stor-jangen Sprint Reverse'],
            [4931.990234375, -5101.59619140625,    'SE, Värmland, Björklangen'],
            [11922.6201171875, -4328.87158203125,  'SE, Värmland, Ransbysäter'],
            [12123.740234375, 2697.36279296875,    'SE, Värmland, Hamra'],
            [12123.5908203125, -5101.78369140625,  'SE, Värmland, Lysvik'],
            [11503.490234375, 562.8009033203125,   'SE, Värmland, Norraskoga'],
            [5248.35986328125, -4328.87158203125,  'SE, Värmland, Älgsjön Sprint'],
            [7058.47998046875, 2696.98291015625,   'SE, Värmland, Elgsjön'],
            [4804.0302734375, -2143.44384765625,   'SE, Värmland, Skogsrallyt'],

            # New England, USA
            [6575.8701171875, -408.4866027832031,  'US, New England, Tolt Valley Sprint Forward'],
            [6701.61962890625, 1521.6917724609375, 'US, New England, Hancock Creek Burst'],
            [6109.5400390625, -353.0966796875,     'US, New England, Hancock Hill Sprint Reverse'],
            [12228.830078125, 1521.5872802734375,  'US, New England, North Fork Pass'],
            [12276.1201171875, 27.728849411010742, 'US, New England, North Fork Pass Reverse'],
            [6488.330078125, 27.087112426757812,   'US, New England, Fuller Mountain Descent'],
            [6468.2998046875, 2768.10107421875,    'US, New England, Fuller Mountain Ascent'],
            [6681.60986328125, 2950.6044921875,    'US, New England, Fury Lake Depart'],
            [12856.66015625, 518.76123046875,      'US, New England, Beaver Creek Trail Forward'],
            [12765.919921875, -4617.37744140625,   'US, New England, Beaver Creek Trail Reverse'],
            [6229.10986328125, 518.7451171875,     'US, New England, Hancock Hill Sprint Forward'],
            [6604.0302734375, -4617.388671875,     'US, New England, Tolt Valley Sprint Reverse'],

            # Catamarca Province, Argentina
            [7667.31982421875, 131.03880310058594,   'AR, Catamarca, Valle de los puentes'],
            [3494.010009765625, -1876.9149169921875, 'AR, Catamarca, Huillaprima'],
            [8265.9501953125, 205.80775451660156,    'AR, Catamarca, Camino a la Puerta'],
            [8256.8603515625, 2581.345947265625,     'AR, Catamarca, Las Juntas'],
            [5303.7900390625, 2581.339599609375,     'AR, Catamarca, Camino de acantilados y rocas'],
            [4171.5, -3227.17626953125,              'AR, Catamarca, San Isidro'],
            [3353.0400390625, 130.6753692626953,     'AR, Catamarca, Miraflores'],
            [2845.6298828125, 206.18272399902344,    'AR, Catamarca, El Rodeo'],
            [7929.18994140625, -3227.17724609375,    'AR, Catamarca, Valle de los puentes a la inversa'],
            [5294.81982421875, 1379.72607421875,     'AR, Catamarca, Camino de acantilados y rocas inverso'],
            [4082.2998046875, -1864.662109375,       'AR, Catamarca, Camino a Coneta'],
            [2779.489990234375, 1344.307373046875,   'AR, Catamarca, La Merced'],

            # Hawkes Bay, New Zealand
            [4799.84033203125, -4415.70703125,      'NZ, Hawkes Bay, Te Awanga Sprint Forward'],
            [11437.0703125, 1789.1517333984375,     'NZ, Hawkes Bay, Ocean Beach'],
            [6624.0302734375, 1789.0382080078125,   'NZ, Hawkes Bay, Ocean Beach Sprint'],
            [4688.52978515625, -2004.0015869140625, 'NZ, Hawkes Bay, Te Awanga Sprint Reverse'],
            [8807.490234375, 2074.951171875,        'NZ, Hawkes Bay, Waimarama Sprint Forward'],
            [6584.10009765625, -1950.1710205078125, 'NZ, Hawkes Bay, Ocean Beach Sprint Reverse'],
            [7137.81005859375, 2892.6181640625,     'NZ, Hawkes Bay, Elsthorpe Sprint Forward'],
            [15844.529296875, 2074.938720703125,    'NZ, Hawkes Bay, Waimarama Point Reverse'],
            [16057.8505859375, 2892.97216796875,    'NZ, Hawkes Bay, Waimarama Point Forward'],
            [11507.4404296875, -4415.119140625,     'NZ, Hawkes Bay, Te Awanga Forward'],
            [8733.98046875, 5268.0849609375,        'NZ, Hawkes Bay, Waimarama Sprint Reverse'],
            [6643.490234375, 5161.06396484375,      'NZ, Hawkes Bay, Elsthorpe Sprint Reverse'],

            # Poland, Leczna County:
            [6622.080078125, 4644.4375,            'PL, Leczna, Czarny Las'],
            [9254.900390625, 1972.7869873046875,   'PL, Leczna, Marynka'],
            [6698.81005859375, -3314.843505859375, 'PL, Leczna, Lejno'],
            [8159.81982421875, 7583.216796875,     'PL, Leczna, Józefin'],
            [7840.1796875, 4674.87548828125,       'PL, Leczna, Kopina'],
            [6655.5400390625, -402.56207275390625, 'PL, Leczna, Jagodno'],
            [13180.3798828125, -3314.898193359375, 'PL, Leczna, Zienki'],
            [16475.009765625, 4674.9150390625,     'PL, Leczna, Zaróbka'],
            [16615.0, 1973.2518310546875,          'PL, Leczna, Zagorze'],
            [13295.6796875, 4644.3798828125,       'PL, Leczna, Jezioro Rotcze'],
            [9194.3203125, 7393.35107421875,       'PL, Leczna, Borysik'],
            [6437.80029296875, -396.1388854980469, 'PL, Leczna, Jezioro Lukie'],

            # Australia, Monaro:
            [13304.1201171875, 2242.524169921875,   'AU, Monaro, Mount Kaye Pass'],
            [13301.109375, -2352.5615234375,        'AU, Monaro, Mount Kaye Pass Reverse'],
            [6951.15966796875, 2242.5224609375,     'AU, Monaro, Rockton Plains'],
            [7116.14990234375, 2457.100341796875,   'AU, Monaro, Rockton Plains Reverse'],
            [6398.90966796875, 2519.408447265625,   'AU, Monaro, Yambulla Mountain Ascent'],
            [6221.490234375, -2352.546630859375,    'AU, Monaro, Yambulla Mountain Descent'],
            [12341.25, 2049.85888671875,            'AU, Monaro, Chandlers Creek'],
            [12305.0400390625, -1280.10595703125,   'AU, Monaro, Chandlers Creek Reverse'],
            [7052.2998046875, -603.9149169921875,   'AU, Monaro, Bondi Forest'],
            [7007.02001953125, -1280.1004638671875, 'AU, Monaro, Taylor Farm Sprint'],
            [5277.02978515625, 2049.85791015625,    'AU, Monaro, Noorinbee Ridge Ascent'],
            [5236.91015625, -565.1859130859375,     'AU, Monaro, Noorinbee Ridge Descent'],

            # Spain, Ribadelles:
            [14348.3603515625, 190.28546142578125,  'ES, Ribadelles, Comienzo en Bellriu'],
            [10568.4296875, -2326.21142578125,      'ES, Ribadelles, Centenera'],
            [7297.27001953125, 2593.36376953125,    'ES, Ribadelles, Ascenso bosque Montverd'],
            [6194.7099609375, -2979.6650390625,     'ES, Ribadelles, Vinedos Dardenya inversa'],
            [6547.39990234375, -2002.0657958984375, 'ES, Ribadelles, Vinedos Dardenya'],
            [6815.4501953125, -2404.635009765625,   'ES, Ribadelles, Vinedos dentro del valle Parra'],
            [10584.6796875, -2001.96337890625,      'ES, Ribadelles, Camina a Centenera'],
            [4380.740234375, -3003.546630859375,    'ES, Ribadelles, Subida por carretera'],
            [6143.5703125, 2607.470947265625,       'ES, Ribadelles, Salida desde Montverd'],
            [7005.68994140625, 190.13796997070312,  'ES, Ribadelles, Ascenso por valle el Gualet'],
            [4562.80029296875, -2326.251708984375,  'ES, Ribadelles, Descenso por carretera'],
            [13164.330078125, -2404.1171875,        'ES, Ribadelles, Final de Bellriu'],

            # Greece, Argolis
            [4860.1904296875, 91.54808044433594,   'GR, Argolis, Ampelonas Ormi'],
            [9666.5, -2033.0767822265625,          'GR, Argolis, Anodou Farmakas'],
            [9665.990234375, 457.1891784667969,    'GR, Argolis, Kathodo Leontiou'],
            [5086.830078125, -2033.0767822265625,  'GR, Argolis, Pomono Ékrixi'],
            [4582.009765625, 164.40521240234375,   'GR, Argolis, Koryfi Dafni'],
            [4515.39990234375, 457.18927001953125, 'GR, Argolis, Fourketa Kourva'],
            [10487.060546875, 504.3974609375,      'GR, Argolis, Perasma Platani'],
            [10357.8798828125, -3672.5810546875,   'GR, Argolis, Tsiristra Théa'],
            [5739.099609375, 504.3973693847656,    'GR, Argolis, Ourea Spevsi'],
            [5383.009765625, -2277.10986328125,    'GR, Argolis, Ypsona tou Dasos'],
            [6888.39990234375, -1584.236083984375, 'GR, Argolis, Abies Koiláda'],
            [6595.31005859375, -3672.58154296875,  'GR, Argolis, Pedines Epidaxi'],

            # Finland, Jämsä
            [7515.40966796875, 39.52613830566406,  'FI, Jämsä, Kailajärvi'],
            [7461.65966796875, 881.0377197265625,  'FI, Jämsä, Paskuri'],
            [7310.5400390625, 846.68701171875,     'FI, Jämsä, Naarajärvi'],
            [7340.3798828125, -192.40794372558594, 'FI, Jämsä, Jyrkysjärvi'],
            [16205.1904296875, 3751.42236328125,   'FI, Jämsä, Kakaristo'],
            [16205.259765625, 833.2575073242188,   'FI, Jämsä, Pitkäjärvi'],
            [8042.5205078125, 3751.42236328125,    'FI, Jämsä, Iso Oksjärvi'],
            [8057.52978515625, -3270.775390625,    'FI, Jämsä, Oksala'],
            [8147.560546875, -3263.315185546875,   'FI, Jämsä, Kotajärvi'],
            [8147.419921875, 833.2575073242188,    'FI, Jämsä, Järvenkylä'],
            [14929.7998046875, 39.52613067626953,  'FI, Jämsä, Kontinjärvi'],
            [14866.08984375, -192.407958984375,    'FI, Jämsä, Hämelahti'],

            # Scotland, UK
            [7144.69970703125, -1657.4295654296875, 'UK, Scotland, Rosebank Farm'],
            [6967.89990234375, 3383.216796875,      'UK, Scotland, Rosebank Farm Reverse'],
            [12857.0703125, 1386.7626953125,        'UK, Scotland, Newhouse Bridge'],
            [12969.2109375, -403.3143310546875,     'UK, Scotland, Newhouse Bridge Reverse'],
            [5822.77001953125, -1157.0889892578125, 'UK, Scotland, Old Butterstone Muir'],
            [5659.8203125, 3339.01513671875,        'UK, Scotland, Old Butterstone Muir Reverse'],
            [7703.72021484375, -403.3154602050781,  'UK, Scotland, Annbank Station'],
            [7587.64013671875, -1839.5506591796875, 'UK, Scotland, Annbank Station Reverse'],
            [5245.4501953125, 1387.3612060546875,   'UK, Scotland, Glencastle Farm'],
            [5238.43994140625, -1860.2203369140625, 'UK, Scotland, Glencastle Farm Reverse'],
            [12583.41015625, -1157.111083984375,    'UK, Scotland, South Morningside'],
            [12670.58984375, -1656.8243408203125,   'UK, Scotland, South Morningside Reverse'],

            # Rallycross locations:
            [1075.0989990234375, 149.30722045898438,  'RX, BE, Mettet'],
            [1400.0770263671875, -230.09457397460938, 'RX, CA, Trois-Rivieres'],
            [1348.85400390625, 101.5931396484375,     'RX, UK, Lydden Hill'],
            [991.1160278320312, -185.40646362304688,  'RX, UK, Silverstone'],
            [1064.97998046875, 195.76113891601562,    'RX, FR, Loheac'],
            [951.51171875, -17.769332885742188,       'RX, DE, Estering'],
            [1287.4329833984375, 134.0433807373047,   'RX, LV, Bikernieki'],
            [1036.0970458984375, 122.2354736328125,   'RX, NO, Hell'],
            [1026.759033203125, -541.3275756835938,   'RX, PT, Montalegre'],
            [1064.623046875, -100.92737579345703,     'RX, ZA, Killarney'],
            [1119.3590087890625, -341.3289794921875,  'RX, ES, Barcalona-Catalunya'],
            [1207.18798828125, 180.26181030273438,    'RX, SE, Holjes'],
            [1194.22900390625, -133.4615936279297,    'RX, AE, Yas Marina'],

            # Test track locations:
            [3601.22998046875, 121.67539978027344, 'DirtFish'],
        ]
    
        self.track_dict = defaultdict(list)
        for t in track_data:
            self.track_dict[t[0]].append((t[1], t[2]))

    def indentify_track(self, length, start_z):
        """
        Identify the track based on the length and start_z.

        Returns the track name
        """

        if start_z is not None and length in self.track_dict.keys():
            track_candidates = self.track_dict[length]
            track_candidates_start_z = np.array([t[0] for t in track_candidates])
            track_candidates_start_z_dist = np.abs(track_candidates_start_z - start_z)
            best_match_id = np.argmin(track_candidates_start_z_dist)
            track_name = track_candidates[best_match_id][1]
        else:
            track_name = 'Unknown'

        return track_name