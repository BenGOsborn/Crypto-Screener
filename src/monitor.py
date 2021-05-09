# This is going to have a class which is responsible for monitoring the prices and such
# Take code for splitting arrays from my previous project
import os
from api import API
import threading

class Monitor:
    def __init__(self, num_symbols):
        self.__stop_flag = [False]
        self.__num_symbols = num_symbols

        token_info = self.__api.get_token_info(num_symbols)
        self.__token_data = {info['id']: {"token_info": info, "price_data": ()} for info in token_info} # Now we can modify the data by the key itself
        self.__token_ids = [info['id'] for info in token_info]

        self.__threads = []

    @staticmethod
    def moon_score(price_data):
        price_rate_1 = price_data[1:] / price_data[:-1]
        price_rate_1_rate = price_rate_1[1:] / price_rate_1[:-1]

        N_STEPS = 5
        price_rate_n = price_data[N_STEPS:] / price_data[:-N_STEPS]
        price_rate_n_rate = price_rate_n[N_STEPS:] / price_rate_n[:-N_STEPS]

        slope_1 = price_rate_1[-1]
        concavity_1 = price_rate_1_rate[-1]
        slope_n = price_rate_n[-1]
        concavity_n = price_rate_n_rate[-1]

        score = (slope_1 ** ((1 - (1 / np.math.sqrt(N_STEPS))) * concavity_1)) * (slope_n ** ((1 / np.math.sqrt(N_STEPS)) * concavity_n))

        return slope_1, concavity_1, slope_n, concavity_n, score

    @staticmethod
    def monitor_tokens(token_ids, token_data, stop_flag):
        api = API()

        while not stop_flag[0]:
            for token_id in token_ids:
                price_data = api.get_price_data(token_id)
                price_data = Monitor.moon_score(price_data)
                token_data[token_id]['price_data'] = price_data
    
    def stop(self):
        self.__stop_flag = [True]

        for thread in self.__threads:
            thread.join()

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

        for group in groups:
            thread = threading.Thread(target=Monitor.monitor_tokens, args=(group, self.__token_data, self.__stop_flag))
            thread.start()
            self.__threads.append(thread)

    def get_data(self, num_data):
        token_data = self.__token_data.copy()

        sorted_tokens = sorted(token_data, key=lambda x: token_data[x]['price_data'][4], reverse=True)

        formatted = [(data['token_info']['name'], data['token_info']['symbol'], *data['price_data'][:4]) for data in list(token_data.values())[:num_data]]

        return formatted

if __name__ == "__main__":
    monitor = Monitor(10)

    monitor.run()