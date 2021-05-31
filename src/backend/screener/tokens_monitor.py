import os
import threading
from time import sleep
import json
from screener.api import API
from screener.token_math import TokenMath

class TokensMonitor:
    """
    Monitors a specified number of tokens and sorts them based on their performance for use

    :param num_tokens An integer that represents the number of tokens to monitor
    :param page_size An integer that represents the number of tokens returned per page
    :param file_path A string that represents the file path of the temporary data sharing file
    """

    def __init__(self, num_tokens, page_size, file_path="tmp.json"):
        self.__num_tokens = num_tokens
        self.__page_size = page_size
        self.__file_path = file_path

        self.__token_data = {}

    @staticmethod
    def update_token_data(num_tokens, token_data):
        """
        Monitors and updates the token data

        :param num_tokens An integer that represents the number of tokens to update
        :param token_data A dictionary that stores the data for the tokens
        """
        api = API()
        header = f"Thread update: "

        print(f"{header}Starting")

        # Update the token data while this thread runs
        while True:
            # Get the token info and ids
            print(f"{header}Updating list of tokens")
            token_info = api.get_token_info(num_tokens)
            valid_token_ids = [info['id'] for info in token_info]

            # If the token id from the token data is not in the new token ids then delete it
            for token_id in token_data.keys():
                if token_id not in valid_token_ids:
                    del token_data[token_id]

            # If a new token id is not in the original token data then add it
            for info in token_info:
                token_id = info['id']
                if token_id not in token_data.keys():
                    token_data[token_id] = {'token_info': info, 'token_data': [-1000 for _ in range(8)], 'init': False}

            # Iterate over each token and update its data
            for token_id in valid_token_ids:
                sleep(0.7)

                try:
                    token_history_raw = api.get_token_history(token_id)
                    token_history_parsed = TokenMath.parse_token_data(token_history_raw)
                    token_data[token_id]['token_id'] = token_history_parsed

                    if not token_data[token_id]['init']:
                        token_data[token_id]['init'] = True
                    
                    print(f"{header}Updated data for token {token_id}")
                
                except Exception as e:
                    print(f"{header}Encountered exception '{e}' for {token_id}")

    @staticmethod
    def write_token_data(data_object, file_path):
        """
        Writes the token data to a shared file

        :param data_object The data object to be written to the file
        :param file_path A string representing the path to the shared data file
        """
        header = f"Thread write: "

        print(f"{header}Starting")

        while True:
            sleep(10)

            try:
                with open(file_path, 'w') as f:
                    json.dump(data_object, f)
                
                print(f"{header}Updated shared data")
            
            except Exception as e:
                print(f"{header}Encountered exception '{e}'")

    @staticmethod
    def read_token_data(data_object, file_path):
        """
        Reads the token data from the shared file

        :param data_object The data object to update with the files data
        :param file_path A string representing the path to the shared data file
        """
        header = f"Thread read: "

        print(f"{header}Starting")

        while True:
            sleep(10)

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data_object.update(data)

                print(f"{header}Updated local data")
            
            except Exception as e:
                print(f"{header}Encountered exception '{e}'")
        
    def stop(self):
        """
        Cleans up the program on exit
        """
        # Delete the shared data file to let future instances of the program know there are no monitor threads
        print("Stopping...")

        if os.path.exists(self.__file_path):
            print("Cleaning up files")

            os.remove(self.__file_path)

    def run(self):
        """
        Spawns the process which updates the token data
        """
        if os.path.exists(self.__file_path): # If the path to the file exists then it means the main update thread is running and we should read from that file which will contain the updated data
            # Create a new daemon thread to run the reader
            print("Initializing read thread...")

            read_thread = threading.Thread(target=TokensMonitor.read_token_data, args=(self.__token_data, self.__file_path))
            read_thread.setDaemon(True)
            read_thread.start()

        else: # If there is no file, it means an updater thread doesnt exist and we need to create one
            with open(self.__file_path, 'w') as f: # Create a new empty file to prevent the other from being made
                pass

            # Create a new daemon thread to run the updater
            print("Initializing monitor thread...")

            monitor_thread = threading.Thread(target=TokensMonitor.update_token_data, args=(self.__num_tokens, self.__token_data))
            monitor_thread.setDaemon(True)
            monitor_thread.start()

            # Create a new daemon thread to run the writer
            print("Initializing write thread...")
            
            write_thread = threading.Thread(target=TokensMonitor.write_token_data, args=(self.__token_data, self.__file_path))
            write_thread.setDaemon(True)
            write_thread.start()

    def get_page_request_info(self):
        """
        Get the data regarding the limits of the current data

        :return A tuple that contains numbers that represent the minimum page that can be requested, the maximum page that can be requested, the number of tokens per page, and the current number of tokens with data
        """
        # Set the minimum number of pages that can be returned (should always be one page)
        page_min = 1

        # Count how many tokens there are that have data
        true_num_tokens = 0
        for values in self.__token_data.values():
            if values['init']:
                true_num_tokens += 1

        # Set the max number of pages given the number of tokens
        page_max = max(true_num_tokens - 1, 1) // self.__page_size + 1

        return page_min, page_max, self.__page_size, true_num_tokens

    def get_page_data(self, page_number, reverse=False):
        """
        Get the tokens for a specific page

        :param page_number An integer that represents the page number of the data to be viewed
        :param reverse A boolean that determines if the tokens and their data should be ordered from best to worst or worst to best

        :return An array containing the data for each token on the specified page
        """
        page_min, page_max, _, _ = self.get_page_request_info()

        assert page_number >= page_min and page_number <= page_max, "Invalid page number!"

        # Calculate the indices that are required to slice the sorted token array to get the right page
        start_index = (page_number - 1) * self.__page_size
        end_index = page_number * self.__page_size

        # Sort the tokens by their moon score ranking in descending order and remove the invalid tokens
        sorted_token_ids = sorted(self.__token_data, key=lambda x: self.__token_data[x]['token_data'][7], reverse=(not reverse))
        valid_tokens = [token_id for token_id in sorted_token_ids if self.__token_data[token_id]['init']][start_index:end_index]

        # Format the layout of the returned token data
        formatted = [[start_index + i + 1, *self.__token_data[token_id]['token_info'].values(), *self.__token_data[token_id]['token_data']] for i, token_id in enumerate(valid_tokens)]

        return formatted

if __name__ == "__main__":
    monitor = TokensMonitor(10, 5)

    monitor.run()

    sleep(10)
    
    data = monitor.get_data(1)
    print(data)

    monitor.stop()
