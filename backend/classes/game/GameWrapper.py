from classes.game.GameHandler import GameHandler
from classes.game.GameDirtRally2 import GameDirtRally2


class GameWrapper:

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