import datetime
import requests
import numpy as np

class API:
    def __init__(self):
        self.__COINGECKO_URL = "https://api.coingecko.com/api/v3"
        self.__VS_CURRENCY = "USD"

        self.__session = requests.Session()

    def get_token_info(self, num_symbols):
        PER_PAGE = 250
        num_pages = (num_symbols - 1) // PER_PAGE + 1

        token_data = []

        for page_number in range(num_pages):
            req_url = f"{self.__COINGECKO_URL}/coins/markets?vs_currency={self.__VS_CURRENCY}&per_page={PER_PAGE}&page={page_number + 1}"
            request = self.__session.get(req_url)

            if request.ok:
                form_data = request.json()
                token_data += [{"id": data['id'], "symbol": data['symbol'], "name": data['name'], "image": data['image']} for data in form_data]
        
        return token_data[:num_symbols]

    def get_price_data(self, symbol_id):
        DAYS = 7
        req_url = f"{self.__COINGECKO_URL}/coins/{symbol_id}/market_chart?vs_currency={self.__VS_CURRENCY}&days={DAYS}"
        request = self.__session.get(req_url) 

        try:
            form_json = request.json()
            price_history = np.array(form_json['prices'])

            return price_history[:, 1]
        
        except:
            None

if __name__ == "__main__":
    api = API()

    token_info = api.get_token_info(10)

    for token in token_info:
        print(token)
        print(api.get_price_data(token['id']).shape)