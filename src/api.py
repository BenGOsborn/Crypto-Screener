import datetime
import requests
import numpy as np

class API:
    def __init__(self):
        self.__KRAKEN_URL = "https://api.kraken.com/0"
        self.__COINGECKO_URL = "https://api.coingecko.com/api/v3"

        self.__session = requests.Session()

    def get_symbols(self, num_symbols, vs_currency="USD"):
        PER_PAGE = 250
        num_pages = (num_symbols - 1) // PER_PAGE + 1

        symbols = []

        for page_number in range(num_pages):
            req_url = f"{self.__COINGECKO_URL}/coins/markets?vs_currency={vs_currency}&per_page={PER_PAGE}&page={page_number + 1}"
            request = self.__session.get(req_url)

            if request.ok:
                form_data = request.json()
                temp_symbols = [token_data['symbol'] for token_data in form_data]
                temp_symbols = [symbol.upper() for symbol in temp_symbols]
                symbols += temp_symbols
        
        return symbols[:num_symbols]

    # KRAKEN API DOES NOT YET SUPPORT BINANCE SMART CHAIN COINS - POSSIBLY CHANGE API IN THE FUTURE
    # It appears this API doesnt work for half of these symbols - Im going to have to find a new API
    def get_price_data(self, symbol, interval=5, symbol_counterpart="USD"):
        pair = symbol + symbol_counterpart

        req_url = f"{self.__KRAKEN_URL}/public/OHLC?pair={pair}&interval={interval}" # By default interval returns the previous 60 hours worth of data
        request = self.__session.get(req_url) 

        try:
            form_json = request.json()
            price_history = np.array(list(form_json['result'].values())[0]).astype(np.float64)

            return price_history
        
        except:
            return np.zeros((720, 8)) # This is the default size of the array

if __name__ == "__main__":
    api = API()

    symbols = api.get_symbols(2000)[-1000:]

    for symbol in symbols:
        print(symbol)
        price_data = api.get_price_data(symbol)
        print(price_data)
        print()