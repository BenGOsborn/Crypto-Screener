from screener.monitor import Monitor
from time import sleep
from tabulate import tabulate

def main(): # Maybe some sort of command line argument here
    NUM_SYMBOLS = 4000
    NUM_SYMBOLS_DISPLAY = 7

    monitor = Monitor(NUM_SYMBOLS)
    monitor.run()

    while True:
        try:
            raw_data = monitor.get_data(0, NUM_SYMBOLS_DISPLAY, reverse=False)
            table_data = [[data['token_info']['name'], data['token_info']['symbol'], data['token_info']['url'], *data['price_data'][:6]] for data in raw_data.values()]

            table = tabulate(table_data, headers=["Name", "Symbol", "URL", "2hr rate", "6hr rate", "12hr rate", "24hr rate", "48hr rate", "Recent price"])
            print(table)
            print()

            sleep(60 * 10)
        
        except KeyboardInterrupt:
            break
    
    monitor.stop()

if __name__ == "__main__":
    main()

