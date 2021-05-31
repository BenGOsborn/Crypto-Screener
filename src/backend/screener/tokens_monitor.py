import os
import threading
from time import sleep
import numpy as np
import json
from screener.api import API
from screener.token_math import TokenMath

# Changes to be made
#  - Put all of the static math functions into their own class
#  - Create a single daemon thread that runs if there is no file, and goes through and gets the files with a pause inbetween
#  - Then after the coins have been monitored, scrape down ALL (not just the fixed amount) of new coins, update the num symbols and modify the dictionary to have the new symbols and remove the old ones

class TokensMonitor:
    def __init__(self, num_symbols, page_size, file_path="tmp.json"):
        self.__num_symbols = num_symbols
        self.__page_size = page_size
        self.__file_path = file_path

        self.__token_data = {}

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
                    token_history_parsed = TokenMath.parse_token_data(token_history)
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

            read_thread = threading.Thread(target=TokensMonitor.read_token_data, args=(self.__token_data, self.__file_path))
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
                monitor_thread = threading.Thread(target=TokensMonitor.update_token_data, args=(group, self.__token_data, i))
                monitor_thread.setDaemon(True)
                monitor_thread.start()

            print("Monitor thread initialization process complete")

            print("Initializing write thread...")
            
            write_thread = threading.Thread(target=TokensMonitor.write_token_data, args=(self.__token_data, self.__file_path))
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

        page_max = max(true_num_symbols - 1, 1) // self.__page_size + 1

        return page_min, page_max, self.__page_size, true_num_symbols

    def get_page_data(self, page_number, reverse=False):
        page_min, page_max, _, _ = self.get_page_request_info()

        assert page_number >= page_min and page_number <= page_max, "Invalid page number!"

        start_index = (page_number - 1) * self.__page_size
        end_index = page_number * self.__page_size

        sorted_token_ids = sorted(self.__token_data, key=lambda x: self.__token_data[x]['token_data'][7], reverse=(not reverse))
        valid_tokens = [token_id for token_id in sorted_token_ids if self.__token_data[token_id]['init']][start_index:end_index]

        formatted = [[start_index + i + 1, *self.__token_data[token_id]['token_info'].values(), *self.__token_data[token_id]['token_data']] for i, token_id in enumerate(valid_tokens)]

        return formatted

if __name__ == "__main__":
    monitor = TokensMonitor(10, 5)

    monitor.run()

    sleep(10)
    
    data = monitor.get_data(1)
    print(data)

    monitor.stop()
