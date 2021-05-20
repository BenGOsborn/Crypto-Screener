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
        self.__file_path = file_path

        self.__token_data = {}

    @staticmethod
    def significant_figures(number, sig_figs):
        return round(number, sig_figs - int(np.math.floor(np.math.log10(abs(number)))) - 1)

    @staticmethod
    def exp_moving_average(data, window):
        kernel = np.exp(np.linspace(-1, 0, window))
        kernel /= kernel.sum()

        return np.convolve(data, kernel, mode='valid')

    @staticmethod
    def parse_token_data(token_history):
        EPSILON = 1e-6
        WINDOW = 12
        DECIMALS = 4

        price_data = token_history[0]
        volume_data = token_history[1]

        recent_price = Monitor.significant_figures(price_data[-1], DECIMALS) if price_data[-1] < 1 else round(price_data[-1], DECIMALS)
        recent_volume = Monitor.significant_figures(volume_data[-1], DECIMALS) if volume_data[-1] < 1 else round(volume_data[-1], DECIMALS)

        CHANGE_PERIODS = [2, 6, 12, 24, 48] # 2 hour change, 6 hour change, 12 hour change, 24 hour change, 48 hour change
        moving_price_changes = [(Monitor.exp_moving_average(price_data, WINDOW)[period:] / (Monitor.exp_moving_average(price_data, WINDOW)[:-period] + EPSILON))[-1] for period in CHANGE_PERIODS]
        moving_volume_changes = [(Monitor.exp_moving_average(volume_data, WINDOW)[period:] / (Monitor.exp_moving_average(volume_data, WINDOW)[:-period] + EPSILON))[-1] for period in CHANGE_PERIODS]

        # ---------------------------- Moon Score calculations -----------------------------------------

        # Base moon score
        moon_score = np.math.log(np.mean(volume_data[:CHANGE_PERIODS[-1]]), 1e+6)

        # Represent the powers of the denominators of the price and the volume weights
        normalizing_price_power = sum([np.math.pow(change_period, 0.5) / np.math.pow(len(CHANGE_PERIODS), 2) for change_period in CHANGE_PERIODS])
        normalizing_volume_power = sum([np.math.pow(change_period, 0.25) / np.math.pow(len(CHANGE_PERIODS), 2) for change_period in CHANGE_PERIODS])

        for moving_price_change, moving_volume_change, reversed_change_period in zip(moving_price_changes, moving_volume_changes, CHANGE_PERIODS[::-1]):
            # Calculate a portion of the moon score and multiply them with the current moon score
            partial_price = (moving_price_change ** np.math.pow(reversed_change_period, 0.5)) / (moving_price_change ** normalizing_price_power)
            partial_volume = (moving_volume_change ** np.math.pow(reversed_change_period, 0.25)) / (moving_volume_change ** normalizing_volume_power)

            moon_score *= partial_price * partial_volume

        # ---------------------------- End of Moon Score calculations -----------------------------------------

        price_changes = [Monitor.significant_figures(((price_data[period:] / (price_data[:-period] + EPSILON))[-1] - 1) * 100, DECIMALS) for period in CHANGE_PERIODS]
        
        return price_changes + [recent_price, recent_volume, moon_score]

    @staticmethod
    def update_token_data(token_ids, token_data, thread_id):
        api = API()
        header = f"Thread update {thread_id}: "

        print(f"{header}Launched and ready to start")
        sleep(60)
        print(f"{header}Starting")

        while True:
            for token_id in token_ids:
                try:
                    token_history = api.get_token_history(token_id)
                    token_history_parsed = Monitor.parse_token_data(token_history)
                    token_data[token_id]['token_data'] = token_history_parsed
                    
                    if not token_data[token_id]['init']:
                        token_data[token_id]['init'] = True

                    print(f"{header}Updated data for {token_id}")

                except Exception as e:
                    print(f"{header}Encountered exception '{e}' for {token_id}")
                
                sleep(8) # Prevents reaching the rate limit of 100 for the API

    @staticmethod
    def write_token_data(data_object, file_path):
        header = f"Thread write 0: "

        print(f"{header}Launched and ready to start")
        sleep(60)
        print(f"{header}Starting")

        while True:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data_object, f)
                
                print(f"{header}Updated shared data")
            
            except Exception as e:
                print(f"{header}Encountered exception '{e}'")

            sleep(6)

    @staticmethod
    def read_token_data(data_object, file_path):
        header = f"Thread read 0: "

        print(f"{header}Launched and ready to start")
        sleep(60)
        print(f"{header}Starting")

        while True:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data_object.update(data)

                print(f"{header}Updated local data")
            
            except Exception as e:
                print(f"{header}Encountered exception '{e}'")
            
            sleep(6)
        
    def stop(self):
        print("Stopping...")

        if os.path.exists(self.__file_path):
            print("Cleaning up files")

            os.remove(self.__file_path)

    def run(self):
        # On every deployment, the temp file manually deleted before launching the app - this is done automatically in Heroku

        if os.path.exists(self.__file_path):
            print("Initializing read threads...")

            read_thread = threading.Thread(target=Monitor.read_token_data, args=(self.__token_data, self.__file_path))
            read_thread.setDaemon(True)
            read_thread.start()

            print("Read thread initialization process complete")

        else:
            with open(self.__file_path, 'w') as f: # Create a new empty file to prevent the other from being made
                pass

            print("Initializing monitor threads...")

            api = API()
            token_info = api.get_token_info(self.__num_symbols)
            self.__token_data = {info['id']: {'token_info': info, 'token_data': [-1000 for _ in range(8)], 'init': False} for info in token_info}

            token_ids = [info['id'] for info in token_info]

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
                monitor_thread = threading.Thread(target=Monitor.update_token_data, args=(group, self.__token_data, i))
                monitor_thread.setDaemon(True)
                monitor_thread.start()

            print("Monitor thread initialization process complete")

            print("Initializing write thread...")
            
            write_thread = threading.Thread(target=Monitor.write_token_data, args=(self.__token_data, self.__file_path))
            write_thread.setDaemon(True)
            write_thread.start()

            print("Write thread initialization process complete")

    # --------------------------------------------------------------------------------------------------------------------------

    def get_page_request_info(self):
        page_min = 1

        true_num_symbols = 0
        for values in self.__token_data.values():
            if values['init']:
                true_num_symbols += 1

        page_max = np.max(true_num_symbols - 1, 1) // self.__page_size + 1

        return page_min, page_max, self.__page_size, true_num_symbols

    def get_page_data(self, page_number, reverse=False):
        assert page_number >= self.__PAGE_MIN and page_number <= self.__PAGE_MAX, "Invalid page number!"

        start_index = (page_number - 1) * self.__page_size
        end_index = page_number * self.__page_size

        sorted_token_ids = sorted(self.__token_data, key=lambda x: self.__token_data[x]['token_data'][7], reverse=(not reverse))
        valid_tokens = [token_id for token_id in sorted_token_ids if self.__token_data[token_id]['init']][start_index:end_index]

        formatted = [[start_index + i + 1, *self.__token_data[token_id]['token_info'].values(), *self.__token_data[token_id]['token_data']] for i, token_id in enumerate(valid_tokens)]

        return formatted

if __name__ == "__main__":
    monitor = Monitor(10, 5)

    monitor.run()

    sleep(10)
    
    data = monitor.get_data(1)
    print(data)

    monitor.stop()
