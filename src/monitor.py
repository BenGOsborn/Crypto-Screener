# This is going to have a class which is responsible for monitoring the prices and such
# Take code for splitting arrays from my previous project
from api import API

class Monitor:
    def __init__(self, num_symbols):
        self.__api = API()

        self.__stop_flag = [False]
        self.__num_symbols = num_symbols

        self.__token_data = self.__api.get_token_data(num_symbols)

        # I need some way of linking the moon score and the token together, should be easy?
