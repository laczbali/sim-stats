from flask import Flask, request
from flask_cors import CORS
import logging

from classes.webapi.JsonResponse import JsonResponse
from classes.game.GameWrapper import GameWrapper

class FlaskApp:

    # set up flask app
    app: Flask = Flask(__name__)
    cors: CORS = CORS(
            app,
            origins=["http://127.0.0.1"],
            supports_credentials=True
    )

    # disable logging of API calls
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    


    @app.route("/test")
    def test():
        """
        Basic sanity check
        """
        return JsonResponse.make_response("HelloWorld to " + request.remote_addr)



    @app.route("/game/list")
    def get_game_list():
        """
        Returns the list of supported games
        """
        return JsonResponse.make_response(GameWrapper.get_game_list())



    @app.route("/game/attributes")
    def get_game_attributes():
        """
        Returns the attributes and saved values of a game
        """
        
        # get game name from query parameters of request
        game_name = request.args.get("name")

        # return attributes of game
        return JsonResponse.make_response(GameWrapper.get_game_attributes(game_name))



    @app.route("/game/start", methods=["POST"])
    def start_run():
        """
        Starts a new run of a game
        """

        # get parameters from request
        parameters = request.get_json()

        # check that the game_name is given
        if parameters == None or "game_name" not in parameters:
            return JsonResponse.make_response("No game_name given")

        # start the run
        return JsonResponse.make_response(GameWrapper.start_run(parameters))



    @app.route("/game/stop", methods=["POST"])
    def stop_run():
        """
        Stops the current run of a game
        """

        # stop the run
        return JsonResponse.make_response(GameWrapper.stop_run())


    
    @app.route("/game/status")
    def get_run_status():
        """
        Returns the status of the current run
        """

        # get status of the run
        return JsonResponse.make_response(GameWrapper.get_run_status())


    
    @app.route("/game/process", methods=["POST"])
    def process_run():
        """
        Processes the current run
        """

        # get parameters from request
        parameters = request.get_json()

        # check that the mode is given
        if parameters == None or "mode" not in parameters:
            return JsonResponse.make_response("No mode given")

        # process the run
        return JsonResponse.make_response(GameWrapper.process_run(parameters))