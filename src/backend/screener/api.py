import requests
from time import sleep
import numpy as np

class API:
    """
    Fetches token data from the CoinGecko API
    """

    def __init__(self):
        self.__COINGECKO_URL = "https://api.coingecko.com/api/v3"
        self.__VS_CURRENCY = "USD"

        self.__session = requests.Session()

    def get_token_info(self, num_tokens):
        """
        Gets the information for a given number of tokens

        :param num_tokens A number that represents the number of tokens to return information for

        :return An array containing the information for each token
        """
        print(f"Getting token info for {num_tokens} tokens")

        PER_PAGE = 250
        num_pages = (num_tokens - 1) // PER_PAGE + 1

        token_info = []

        for page_number in range(num_pages):
            req_url = f"{self.__COINGECKO_URL}/coins/markets?vs_currency={self.__VS_CURRENCY}&per_page={PER_PAGE}&page={page_number + 1}"
            request = self.__session.get(req_url)

            if request.ok:
                form_json = request.json()
                token_info += [{'id': data['id'], 'symbol': data['symbol'], 'name': data['name'], 'url': f"https://www.coingecko.com/en/coins/{data['id']}", 'image': data['image']} for data in form_json]

            sleep(0.7) # Cooldown timer to prevent the API from blocking the server

        token_info = token_info[:num_tokens]

        print(f"Got token info for {len(token_info)} tokens. Missing: {num_tokens - len(token_info)}")
        
        return token_info

    def get_token_history(self, token_id, days=7):
        """ 
        Gets the price and 24h volume history of a specified token

        :param token_id A string that is the ID of the token to get the data of
        :param days An integer that represents the number of days to return data for

        :return An array that contains the price and 24h volume data for the specified number of days with hourly intervals
        """ 
        assert days > 1, "Number of days must be greater then 1"

        req_url = f"{self.__COINGECKO_URL}/coins/{token_id}/market_chart?vs_currency={self.__VS_CURRENCY}&days={days}"
        request = self.__session.get(req_url) 

        if request.ok:
            form_json = request.json()
            token_data = np.array([form_json['prices'], form_json['total_volumes']])

            return token_data[:, :, 1] # Remove the column that contains the times the events occured

if __name__ == "__main__":
    api = API()

    print(api.get_token_info(20))

