# This is going to have a class which is responsible for monitoring the prices and such
# Take code for splitting arrays from my previous project
import os
from api import API

class Monitor:
    def __init__(self, num_symbols):
        self.__api = API()

        self.__stop_flag = [False]
        self.__num_symbols = num_symbols

        token_info = self.__api.get_token_info(num_symbols)
        self.__token_data = {info['id']: {"token_info": info, "price_data": ()} for info in token_info} # Now we can modify the data by the key itself
        self.__token_ids = [info['id'] for info in token_info]

    def run(self):
        num_cores = os.cpu_count()
        total_items = len(self.__token_ids)

        # Now I need to get how many bots can go into the cores as well as the remainder
        per_core = total_items // num_cores
        remainders = total_items % num_cores # If there is not enough for the cores then this should be in its own seperate group

        cutoff_point = per_core * num_cores
        split_group1 = self.__token_ids[:cutoff_point]
        split_group2 = self.__token_ids[cutoff_point:]

        groups = []
        if per_core > 0:
            for i in range(num_cores):
                group = split_group1[i * per_core:(i + 1) * per_core]
                groups.append(group)
            
            # Now I need to do something with the remainders
            for i in range(remainders):
                groups[i].append(split_group2[i])

        else:
            for i in range(remainders):
                groups.append(split_group2[i])

        print(groups)

    def get_data(self, num_data):
        token_data = self.__token_data.copy()

        sorted_tokens = sorted(token_data, key=lambda x: token_data[x]['price_data'][4], reverse=True)

        formatted = [(data['token_info']['name'], data['token_info']['symbol'], *data['price_data'][:4]) for data in list(token_data.values())[:num_data]]

        return formatted

if __name__ == "__main__":
    monitor = Monitor(10)

    monitor.run()