from classes.game.RunData import RunData
from classes.game.GameHandler import GameHandler, GameHandlerProcessMode, GameHandlerState
from classes.game.GameDirtRally2 import GameDirtRally2


class GameWrapper:

    game_instance: GameHandler = None

    def get_game_list():
        """
        Returns the list of supported games
        """

        # get all classes that inherit from GameHandler (only works for classes that are imported here)
        game_classes = GameHandler.__subclasses__()

        # return class names
        return list(
            map(
                lambda x: x.__name__.replace("Game", ""),
                game_classes
            )
        )



    def get_game_attributes(game_name: str):
        """
        Returns the attributes and saved data of a game
        """

        #  get all classes that inherit from GameHandler (only works for classes that are imported here)
        game_classes = GameHandler.__subclasses__()

        # get the class that matches the game name
        game_class = list(
            filter(
                lambda x: x.__name__.replace("Game", "") == game_name,
                game_classes
            )
        )[0]

        # return the attributes of the class
        return game_class.get_attributes()



    def start_run(parameters):
        """
        Starts a new run of a game
        """
        try:
            # shut down previous instance
            if GameWrapper.game_instance is not None:
                GameWrapper.game_instance.shutdown()

            # get game_name
            game_name = parameters["game_name"]

            #  get all classes that inherit from GameHandler (only works for classes that are imported here)
            game_classes = GameHandler.__subclasses__()

            # get the class that matches the game name
            game_class: GameHandler = list(
                filter(
                    lambda x: x.__name__.replace("Game", "") == game_name,
                    game_classes
                )
            )[0]

            # set up RunData (if keys other than the game_name are present)
            if len(list(parameters.keys())) > 1:
                run_data = RunData()
                run_data.set_parameters(parameters)
            else:
                run_data = None

            # start the run
            GameWrapper.game_instance: GameHandler = game_class()
            GameWrapper.game_instance.start_run(run_data)

            return "ok"

        except Exception as e:
            return "Could not start run" + "\n" + str(e)



    def stop_run():
        """
        Stops the current run of a game
        """
        try:
            # shut down previous instance
            if GameWrapper.game_instance is not None:
                GameWrapper.game_instance.shutdown()

            return "ok"

        except Exception as e:
            return "Could not stop run" + "\n" + str(e)



    def get_run_status():
        """
        Returns the status of the current run
        """
        try:
            response = {}

            # get status of the run
            state = GameWrapper.game_instance.get_state()
            response["state"] = str(state.name)

            # add results to response, if finished
            if state == GameHandlerState.FINISHED:
                response["results"] = GameWrapper.game_instance.get_run_result()

            return response


        except Exception as e:
            return "Could not get run status" + "\n" + str(e)



    def process_run(parameters):

        mode = GameHandlerProcessMode[parameters["mode"]]

        if len(list(parameters.keys())) > 1:
            edited_data = GameWrapper.game_instance.get_run_result()
            edited_data.set_parameters(parameters)
        else:
            edited_data = None

        GameWrapper.game_instance.process_run(mode, edited_data)
        return "ok"