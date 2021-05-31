import datetime
import requests
from time import sleep
import numpy as np

class API:
    def __init__(self):
        self.__COINGECKO_URL = "https://api.coingecko.com/api/v3"
        self.__VS_CURRENCY = "USD"

        self.__session = requests.Session()

    def get_token_info(self, num_tokens):
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

        # -------------------------- THIS HAS PROBLEMS TO DO WITH THE PAGE SIZE ----------------------------------------
        print(f"Got token info for {len(token_info)} tokens. Missing: {num_tokens - len(token_info)}")
        
        return token_info[:num_tokens]

    def get_token_history(self, token_id):
        DAYS = 7
        req_url = f"{self.__COINGECKO_URL}/coins/{token_id}/market_chart?vs_currency={self.__VS_CURRENCY}&days={DAYS}"
        request = self.__session.get(req_url) 

        if request.ok:
            form_json = request.json()
            token_data = np.array([form_json['prices'], form_json['total_volumes']])

            return token_data[:, :, 1] # Remove the column that contains the times the events occured

if __name__ == "__main__":
    api = API()

    print(api.get_token_info(20))

