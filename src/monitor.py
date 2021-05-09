# This is going to have a class which is responsible for monitoring the prices and such
# Take code for splitting arrays from my previous project
from api import API

class Monitor:
    def __init__(self, num_symbols):
        self.__api = API()

        self.__stop_flag = [False]
        self.__num_symbols = num_symbols

        token_info = self.__api.get_token_info(num_symbols)

        self.__token_data = {info['id']: {"token_info": info, "price_data": ()} for info in token_info} # Now we can modify the data by the key itself

        print(self.__token_data)

    def get_data(self, num_data):
        token_data = self.__token_data.copy()

        sorted_tokens = sorted(token_data, key=lambda x: token_data[x]['price_data'][4], reverse=True)

        formatted = [(data['token_info']['name'], data['token_info']['symbol'], *data['price_data'][:4]) for data in list(token_data.values())[:num_data]]

        return formatted


if __name__ == "__main__":
    monitor = Monitor(10)

    print(monitor.get_data(5))