import os
import threading
from time import sleep
import numpy as np
import json
from screener.api import API

class Monitor:
    def __init__(self, num_symbols, page_size, file_path="tmp.json"):
        self.__num_symbols = num_symbols
        self.__page_size = page_size
        self.__PAGE_MIN = 1
        self.__PAGE_MAX = (self.__num_symbols - 1) // self.__page_size + 1
        self.__file_path = file_path

        self.__token_data = {}
        self.__threads = []
        self.__stop_flag = [False]

    @staticmethod
    def significant_figures(number, sig_figs):
        return round(number, sig_figs - int(np.math.floor(np.math.log10(abs(number)))) - 1)

    @staticmethod
    def exp_moving_average(data, window):
        kernel = np.exp(np.linspace(-1, 0, window))
        kernel /= kernel.sum()

        return np.convolve(data, kernel, mode='valid')

    @staticmethod
    def parse_price_data(price_data):
        EPSILON = 1e-6
        WINDOW = 12

        recent_price = Monitor.significant_figures(price_data[-1], 3) if price_data[-1] < 1 else round(price_data[-1], 3)

        CHANGE_PERIODS = [2, 6, 12, 24, 48] # 2 hour change, 6 hour change, 12 hour change, 24 hour change, 48 hour change
        price_changes = [Monitor.significant_figures(((price_data[period:] / (price_data[:-period] + EPSILON))[-1] - 1) * 100, 3) for period in CHANGE_PERIODS]
        moving_price_changes = [(Monitor.exp_moving_average(price_data, WINDOW)[period:] / (Monitor.exp_moving_average(price_data, WINDOW)[:-period] + EPSILON))[-1] for period in CHANGE_PERIODS]

        moon_score = 1
        for price_change, reversed_change_period in zip(moving_price_changes, CHANGE_PERIODS[::-1]):
            partial_moon_score = price_change ** (reversed_change_period ** 0.5)
            moon_score *= partial_moon_score
        
        return price_changes + [recent_price, moon_score]

    @staticmethod
    def update_token_data(token_ids, token_data, stop_flag, thread_id):
        api = API()
        header = f"Thread update {thread_id}: "

        print(f"{header}Launched and ready to start")
        sleep(60)
        print(f"{header}Starting")

        while not stop_flag[0]:
            for token_id in token_ids:
                try:
                    price_data = api.get_price_data(token_id)
                    price_data_parsed = Monitor.parse_price_data(price_data)
                    token_data[token_id]['price_data'] = price_data_parsed
                    
                    if not token_data[token_id]['init']:
                        token_data[token_id]['init'] = True

                    print(f"{header}Updated data for {token_id}")

                except Exception as e:
                    print(f"{header}Encountered exception '{e}' for {token_id}")
                
                sleep(6) # Prevents reaching the rate limit of 100 for the API

    @staticmethod
    def write_token_data(data_object, file_path, stop_flag):
        header = f"Thread write 0: "

        print(f"{header}Launched and ready to start")
        sleep(60)
        print(f"{header}Starting")

        while not stop_flag[0]:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data_object, f)
                
                print(f"{header}Updated shared data")
            
            except Exception as e:
                print(f"{header}Encountered exception '{e}'")

            sleep(60)

    @staticmethod
    def read_token_data(data_object, file_path, stop_flag):
        header = f"Thread read 0: "

        print(f"{header}Launched and ready to start")
        sleep(60)
        print(f"{header}Starting")

        while not stop_flag[0]:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data_object.update(data)

                print(f"{header}Updated local data")
            
            except Exception as e:
                print(f"{header}Encountered exception '{e}'")
            
            sleep(60)
        
    def stop(self):
        print("Stopping threads")

        self.__stop_flag[0] = True

        for thread in self.__threads:
            thread.join()

    def run(self):
        # On every deployment, the temp file manually deleted before launching the app - this is done automatically in Heroku

        if os.path.exists(self.__file_path):
            print("Initializing read threads...")

            read_thread = threading.Thread(target=Monitor.read_token_data, args=(self.__token_data, self.__file_path, self.__stop_flag))
            read_thread.start()
            self.__threads.append(read_thread)

            print("Read thread initialization process complete")

        else:
            with open(self.__file_path, 'w') as f: # Create a new empty file to prevent the other from being made
                pass

            print("Initializing monitor threads...")

            api = API()
            token_info = api.get_token_info(self.__num_symbols)
            self.__token_data = {info['id']: {'token_info': info, 'price_data': [-1000 for _ in range(7)], 'init': False} for info in token_info}

            self.__stop_flag[0] = False

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

            for i, group in enumerate(groups):
                monitor_thread = threading.Thread(target=Monitor.update_token_data, args=(group, self.__token_data, self.__stop_flag, i))
                monitor_thread.start()
                self.__threads.append(monitor_thread)

            print("Monitor thread initialization process complete")

            print("Initializing write thread...")
            
            write_thread = threading.Thread(target=Monitor.write_token_data, args=(self.__token_data, self.__file_path, self.__stop_flag))
            write_thread.start()
            self.__threads.append(write_thread)

            print("Write thread initialization process complete")

    # --------------------------------------------------------------------------------------------------------------------------

    def get_page_request_info(self):
        return self.__PAGE_MIN, self.__PAGE_MAX, self.__page_size, self.__num_symbols

    def get_page_data(self, page_number, reverse=False):
        assert page_number >= self.__PAGE_MIN and page_number <= self.__PAGE_MAX, "Invalid page number!"

        start_index = (page_number - 1) * self.__page_size
        end_index = page_number * self.__page_size

        sorted_token_ids = sorted(self.__token_data, key=lambda x: self.__token_data[x]['price_data'][6], reverse=(not reverse))
        valid_tokens = [token_id for token_id in sorted_token_ids if self.__token_data[token_id]['init']][start_index:end_index]

        formatted = [[start_index + i + 1, *self.__token_data[token_id]['token_info'].values(), *self.__token_data[token_id]['price_data']] for i, token_id in enumerate(valid_tokens)]

        return formatted
    
    # !!!!!!!!!!!!!!!!!! This method is unused and untested !!!!!!!!!!!!!!!!!!
    def get_token_data(self, given_token_id, reverse=False):
        sorted_token_ids = sorted(self.__token_data, key=lambda x: self.__token_data[x]['price_data'][6], reverse=(not reverse))
        valid_tokens = [token_id for token_id in sorted_token_ids if self.__token_data[token_id]['init']]

        indexed = {token_id: {'index': i + 1, **self.__token_data[token_id]} for i, token_id in enumerate(valid_tokens)}

        data_dic = indexed[given_token_id]
        formatted = [data_dic['index'], *data_dic['token_info'].values(), *data_dic['price_data']]

        return formatted

if __name__ == "__main__":
    monitor = Monitor(100, 5)

    monitor.run()

    sleep(10)
    
    data = monitor.get_data(5)
    print([(dic['token_info']['symbol'], dic['price_data'][6]) for dic in data])

    monitor.stop()
