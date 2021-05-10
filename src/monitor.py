import os
import threading
from api import API

class Monitor:
    def __init__(self, num_symbols):
        self.__stop_flag = [False]
        self.__num_symbols = num_symbols

        token_info = self.__api.get_token_info(num_symbols)
        self.__token_data = {info['id']: {"token_info": info, "price_data": [-1000 for _ in range(8)]} for info in token_info} # Change the number of -1000s

        self.__threads = []

    @staticmethod
    def parse_token_data(token_data):
        # I want to do a 2 hour change, 6 hour change, 12 hour change, 24 hour change, 48 hour change

        price_data = token_data[0]
        total_volume_data = token_data[1] # Same for this what do they mean?
        volume_data = total_volume_data[1:] - total_volume_data[:-1] # Wait what does this actually mean though???

        recent_price = price_data[-1]
        recent_volume = volume_data[-1]

        CHANGE_PERIODS = [2, 6, 12, 24, 48]
        price_changes = [price_data[period:] / price_data[:-period] for period in CHANGE_PERIODS]
        price_concavities = [cg[period:] / cg[:-period] for cg, period in zip(price_changes, CHANGE_PERIODS)]
        volume_changes = [volume_data[period:] / volume_data[:-period] for period in CHANGE_PERIODS]

        recent_price_changes = [change[-1] for change in price_changes]
        recent_price_concavities = [concavity[-1] for concavity in price_concavities]
        recent_volume_changes = [volume[-1] for volume in volume_changes]

        moon_score = 1
        for price_change, price_concavity, volume_change, reversed_change_period in zip(recent_price_changes, recent_price_concavities, recent_volume_changes, CHANGE_PERIODS[::-1]):
            partial_moon_score = (price_change * price_concavity * volume_change) ** (reversed_change_period ** 0.5)
            moon_score *= partial_moon_score

        return recent_price_changes + [recent_price, recent_volume, moon_score]

    @staticmethod
    def monitor_tokens(token_ids, token_data, stop_flag):
        api = API()

        while not stop_flag[0]:
            for token_id in token_ids:
                price_data = api.get_price_data(token_id)

                if price_data != None:
                    price_data = Monitor.parse_price_data(price_data)
                    token_data[token_id]['price_data'] = price_data
    
    def stop(self):
        self.__stop_flag = [True]

        for thread in self.__threads:
            thread.join()

    def run(self):
        token_ids = list(self.__token_data.keys())

        num_cores = os.cpu_count()
        total_items = len(token_ids)

        # Now I need to get how many bots can go into the cores as well as the remainder
        per_core = total_items // num_cores
        remainders = total_items % num_cores # If there is not enough for the cores then this should be in its own seperate group

        cutoff_point = per_core * num_cores
        split_group1 = token_ids[:cutoff_point]
        split_group2 = token_ids[cutoff_point:]

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

        formatted = [(data['token_info']['name'], data['token_info']['symbol'], *data['price_data']) for data in list(token_data.values())[:num_data]] # The data returned here needs to be modified

        return formatted

if __name__ == "__main__":
    monitor = Monitor(10)

    monitor.run()