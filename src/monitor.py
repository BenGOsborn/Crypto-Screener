# This is going to have a class which is responsible for monitoring the prices and such
# Take code for splitting arrays from my previous project
from api import API

class Monitor:
    def __init__(self, num_symbols):
        self.__api = API()

        self.__stop_flag = [False]
        self.__num_symbols = num_symbols

        token_info = self.__api.get_token_info(num_symbols)

        self.__token_data = {info['id']: {"token_info": info, "price_data": {}} for info in token_info} # Now we can modify the data by the key itself

        # I need some way of linking the moon score and the token together, should be easy?

    def get_data(self, num_data):
        token_data = self.__token_data.copy()

        # Here I am going to properly format the data
        sorted_tokens = sorted(token_data, key=lambda x: -x['price_data']['moon_score'])

        formatted = [] # Now I need some way of getting the values out for this


if __name__ == "__main__":
    monitor = Monitor(10)
