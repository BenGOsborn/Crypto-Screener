from math import inf
import os
from sys import prefix
import threading
from time import sleep
from screener.api import API
from screener.token_math import TokenMath
import redis
import json


class TokensMonitor:
    """
    Monitors a specified number of tokens and sorts them based on their performance for use

    :param num_tokens An integer that represents the number of tokens to monitor
    :param page_size An integer that represents the number of tokens returned per page
    """

    def __init__(self, num_tokens: int, page_size: int, prefix: str = "TOKEN_MONITOR:"):
        # Metadata for the page requests
        self.__num_tokens = num_tokens
        self.__page_size = page_size
        self.__prefix = prefix

        # Connect to redis
        self.__redis = redis.Redis(
            host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"), db=0)

        print("REDIS DETAILS FROM ENV")
        print(os.getenv("REDIS_HOST"), os.getenv(
            "REDIS_PORT"), os.getenv("REDIS_PASSWORD"), 0)
        print("Hello world: " + self.__redis.exists("hello"))

    @staticmethod
    def __update_token_data(num_tokens: int, prefix: str, redis: redis.Redis):
        """
        Monitors and updates the token data

        :param num_tokens An integer that represents the number of tokens to update
        :param token_data A dictionary that stores the data for the tokens
        """

        # Initialize a new instance of the API
        api = API()

        # Timing constants
        TOKEN_EXPIRY = 60 * 20
        API_COOLDOWN_REST = 0.7

        # Thread log header
        header = f"Thread update: "
        print(f"{header}Starting monitor")

        # Update the token data while this thread runs
        while True:
            # Get the token info and ids
            print(f"{header}Updating list of tokens")
            token_info_list = api.get_token_info(num_tokens)

            # Iterate over each token and update its data
            for token_info in token_info_list:
                # Avoid API cooldown
                sleep(API_COOLDOWN_REST)

                # Get the token ID
                token_id = token_info["id"]

                # If the token does not exist, then add its data
                if not redis.exists(f"{prefix}{token_id}"):
                    try:
                        # Get the raw token history, parse its data then update the global data for that token
                        token_history_parsed = TokenMath.parse_token_data(
                            api.get_token_history(token_id))

                        # Combine the info about the token with the parsed data and store it in redis
                        combined_data = {**token_info, **token_history_parsed}
                        redis.set(f"{prefix}{token_id}", json.dumps(
                            combined_data), ex=TOKEN_EXPIRY)
                        print(f"{header}Updated data for token {token_id}")

                    except Exception as e:
                        # Log the error message
                        print(
                            f"{header}Encountered exception '{e}' for {token_id}")

    def monitor(self):
        """
        Spawns the process which updates the token data
        """

        # Create a new daemon thread and start the updater
        monitor_thread = threading.Thread(
            target=TokensMonitor.__update_token_data, args=(self.__num_tokens, self.__prefix, self.__redis))
        monitor_thread.setDaemon(True)
        monitor_thread.start()

    def get_page_request_info(self):
        """
        Get the data regarding the limits of the current data

        :return A tuple that contains numbers that represent the minimum page that can be requested, the maximum page that can be requested, the number of tokens per page, and the current number of tokens with data
        """

        # Set the minimum number of pages that can be returned (should always be one page)
        PAGE_MIN = 1

        # Count how many tokens there are
        true_num_tokens = 0
        for key in self.__redis.scan_iter():
            if key[:len(self.__prefix)] == self.__prefix:
                true_num_tokens += 1

        # Set the max number of pages given the number of tokens
        page_max = max(true_num_tokens - 1, 1) // self.__page_size + 1

        return PAGE_MIN, page_max, self.__page_size, true_num_tokens

    def get_page_data(self, page_number: int, reverse: bool = False):
        """
        Get the tokens for a specific page

        :param page_number An integer that represents the page number of the data to be viewed
        :param reverse A boolean that determines if the tokens and their data should be ordered from best to worst or worst to best

        :return An array containing the data for each token on the specified page
        """

        # Get the page request info for accepted page numbers and number of tokens
        page_min, page_max, _, true_num_tokens = self.get_page_request_info()

        # Check that the page number is valid
        assert page_number >= page_min and page_number <= page_max, "Invalid page number!"

        # Get the data from redis if the key matches the prefix
        token_data = []
        for key in self.__redis.scan_iter():
            if key[:len(self.__prefix)] == self.__prefix:
                token_data.append(json.loads(
                    self.__redis.get(key[len(self.__prefix):])))

        # Calculate the indices that are required to slice the sorted token array to get the right page
        start_index = (page_number - 1) * self.__page_size
        end_index = page_number * self.__page_size

        # Sort the tokens by their moon score ranking in descending order
        sorted_token_data = sorted(token_data, key=lambda x: token_data[x]["moon_score"], reverse=(
            not reverse))[start_index:end_index]

        # Index the rows and return them
        indexed = [{"index": start_index + i + 1 if not reverse else true_num_tokens -
                    start_index - i, **data} for i, data in enumerate(sorted_token_data)]
        return indexed
