import datetime
import requests
import numpy as np

class API:
    def __init__(self, vs_currency="usd"):
        self.__COINGECKO_URL = "https://api.coingecko.com/api/v3"
        self.__vs_currency = vs_currency

        self.__session = requests.Session()

    def get_token_data(self, num_symbols):
        PER_PAGE = 250
        num_pages = (num_symbols - 1) // PER_PAGE + 1

        token_data = []

        for page_number in range(num_pages):
            req_url = f"{self.__COINGECKO_URL}/coins/markets?vs_currency={self.__vs_currency}&per_page={PER_PAGE}&page={page_number + 1}"
            request = self.__session.get(req_url)

            if request.ok:
                form_data = request.json()
                print(form_data)
                token_data += [(data['id'], data['symbol'], data['name']) for data in form_data]
        
        return token_data[:num_symbols]

    def get_price_data(self, symbol_id):
        req_url = f"{self.__COINGECKO_URL}/coins/{symbol_id}/market_chart?vs_currency={self.__vs_currency}&days={1}" # By default interval returns the previous 60 hours worth of data
        request = self.__session.get(req_url) 

        try:
            form_json = request.json()
            price_history = np.array(form_json['prices'])

            return price_history[:, 1] # Only return the prices as a 1d array
        
        except:
            return np.zeros(289) # This is the default size of the array - it will be used as blank

if __name__ == "__main__":
    api = API()

    symbol_ids = api.get_token_data(10)

    for symbol_id in symbol_ids:
        print(symbol_id)
        price_data = api.get_price_data(symbol_id)
        print(price_data.shape)