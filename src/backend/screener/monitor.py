import os
import threading
from time import sleep
import numpy as np
from screener.api import API

class Monitor:
    def __init__(self, num_symbols, page_size):
        self.__stop_flag = [False]

        self.__num_symbols = num_symbols
        self.__page_size = page_size

        api = API()
        token_info = api.get_token_info(num_symbols)
        self.__token_data = {info['id']: {'token_info': info, 'price_data': [-1000 for _ in range(7)], 'init': False} for info in token_info}

        self.__threads = []

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
        SIG_FIGS = 4

        recent_price = Monitor.significant_figures(price_data[-1], SIG_FIGS)

        CHANGE_PERIODS = [2, 6, 12, 24, 48] # 2 hour change, 6 hour change, 12 hour change, 24 hour change, 48 hour change
        price_changes = [Monitor.significant_figures((price_data[period:] / (price_data[:-period] + EPSILON))[-1] - 1, SIG_FIGS) for period in CHANGE_PERIODS]
        moving_price_changes = [(Monitor.exp_moving_average(price_data, WINDOW)[period:] / (Monitor.exp_moving_average(price_data, WINDOW)[:-period] + EPSILON))[-1] for period in CHANGE_PERIODS]

        moon_score = 1
        for price_change, reversed_change_period in zip(moving_price_changes, CHANGE_PERIODS[::-1]):
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
                    
                    if not token_data[token_id]['init']:
                        token_data[token_id]['init'] = True

                except Exception as e:
                    continue
                
                sleep(3)
    
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

    # --------------------------------------------------------------------------------------------------------------------------

    # I want methods that do the splicing operations for the others - probably just turn the initialization into the constructor instead
    def get_page_request_info(self, page_number):
        page_max = self.__num_symbols // self.__page_size + 1 # The plus one is necessary because that way if there is 1 extra then it technically requires an extra page

        # Now calculate the slice indices from the page number

    def get_data(self, page_number, reverse=False):
        # Now I need some way of getting the start index and the end index

        sorted_token_ids = sorted(self.__token_data, key=lambda x: self.__token_data[x]['price_data'][6], reverse=(not reverse))
        valid_tokens = [token_id for token_id in sorted_token_ids if self.__token_data[token_id]['init']][start_index:end_index]

        formatted = [[i, *self.__token_data[token_id]['token_info'], *self.__token_data[token_id]['price_info']] for i, token_id in enumerate(valid_tokens)]

        return formatted

if __name__ == "__main__":
    monitor = Monitor(100)

    monitor.run()

    sleep(10)
    
    data = monitor.get_data(5)
    print([(dic['token_info']['symbol'], dic['price_data'][6]) for dic in data])

    monitor.stop()
