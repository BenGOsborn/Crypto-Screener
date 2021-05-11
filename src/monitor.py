import os
import threading
from time import sleep
from api import API

class Monitor:
    def __init__(self, num_symbols):
        self.__stop_flag = [False]
        self.__num_symbols = num_symbols

        api = API()
        token_info = api.get_token_info(num_symbols)
        self.__token_data = {info['id']: {"token_info": info, "price_data": [-1000 for _ in range(7)]} for info in token_info}

        self.__threads = []

    @staticmethod
    def parse_price_data(price_data):
        EPSILON = 1e-6

        recent_price = price_data[-1]

        CHANGE_PERIODS = [2, 6, 12, 24, 48] # 2 hour change, 6 hour change, 12 hour change, 24 hour change, 48 hour change
        price_changes = [(price_data[period:] / (price_data[:-period] + EPSILON))[-1] for period in CHANGE_PERIODS]

        moon_score = 1 # Modify the moon score
        for price_change, reversed_change_period in zip(price_changes, CHANGE_PERIODS[::-1]):
            partial_moon_score = price_change ** (reversed_change_period ** 0.5)
            moon_score *= partial_moon_score
        
        return price_changes + [recent_price, moon_score]

    @staticmethod
    def monitor_tokens(token_ids, token_data, stop_flag):
        api = API()

        while not stop_flag[0]:
            for token_id in token_ids:
                try:
                    price_data = api.get_price_data(token_id)

                    price_data_parsed = Monitor.parse_price_data(price_data)
                    token_data[token_id]['price_data'] = price_data_parsed

                except Exception as e:
                    continue

            sleep(60)
    
    def stop(self):
        self.__stop_flag[0] = True

        for thread in self.__threads:
            thread.join()

    def run(self):
        token_ids = list(self.__token_data.keys())

        num_cores = os.cpu_count()
        total_items = len(token_ids)

        per_core = total_items // num_cores
        remainders = total_items % num_cores

        cutoff_point = per_core * num_cores
        split_group1 = token_ids[:cutoff_point]
        split_group2 = token_ids[cutoff_point:]

        groups = []
        if per_core > 0:
            for i in range(num_cores):
                group = split_group1[i * per_core:(i + 1) * per_core]
                groups.append(group)
            
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
        sorted_tokens = sorted(self.__token_data, key=lambda x: self.__token_data[x]['price_data'][6], reverse=True)
        formatted = {token_id: self.__token_data[token_id] for token_id in sorted_tokens[:num_data + 1]}

        return formatted

if __name__ == "__main__":
    monitor = Monitor(100)

    monitor.run()

    sleep(10)
    
    data = monitor.get_data(5)
    print([(dic['token_info']['symbol'], dic['price_data'][6]) for dic in data])

    monitor.stop()
