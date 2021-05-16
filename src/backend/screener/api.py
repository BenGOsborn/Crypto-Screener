import datetime
import requests
from time import sleep
import numpy as np

class API:
    def __init__(self):
        self.__COINGECKO_URL = "https://api.coingecko.com/api/v3"
        self.__VS_CURRENCY = "USD"

        self.__session = requests.Session()

    def get_token_info(self, num_symbols):
        PER_PAGE = 250
        num_pages = (num_symbols - 1) // PER_PAGE + 1

        token_info = []

        for page_number in range(num_pages):
            req_url = f"{self.__COINGECKO_URL}/coins/markets?vs_currency={self.__VS_CURRENCY}&per_page={PER_PAGE}&page={page_number + 1}"
            request = self.__session.get(req_url)

            if request.ok:
                form_data = request.json()
                token_info += [{'id': data['id'], 'symbol': data['symbol'], 'name': data['name'], 'url': f"https://www.coingecko.com/en/coins/{data['id']}", 'image': data['image']} for data in form_data]
            
            sleep(0.6 + 0.1) # Prevents the over spamming of the server by only sending the allowed amount - the +0.1 is to provide a margin of error 

        sleep(60) # This is to reset the rate limit on the API
        
        return token_info[:num_symbols]

    def get_price_data(self, symbol_id):
        DAYS = 7
        req_url = f"{self.__COINGECKO_URL}/coins/{symbol_id}/market_chart?vs_currency={self.__VS_CURRENCY}&days={DAYS}"
        request = self.__session.get(req_url) 

        if request.ok:
            form_json = request.json()
            token_data = np.array(form_json['prices'])

            return token_data[:, 1]

if __name__ == "__main__":
    api = API()

    print(api.get_price_data('csp-dao-network'))