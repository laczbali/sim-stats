from flask import Flask, request
from flask_cors import CORS
import logging

from classes.webapi.JsonResponse import JsonResponse
from classes.game.GameWrapper import GameWrapper

class FlaskApp:

    app: Flask = Flask(__name__)
    cors: CORS = CORS(
            app,
            origins=["http://127.0.0.1"],
            supports_credentials=True
    )
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

        # start the run
        return JsonResponse.make_response(GameWrapper.start_run(parameters))



    @app.route("/game/stop", methods=["POST"])
    def stop_run():
        """
        Stops the current run of a game
        """

        # stop the run
        return JsonResponse.make_response(GameWrapper.stop_run())