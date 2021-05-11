from monitor import Monitor
from time import sleep
from tabulate import tabulate

def main(): # Maybe some sort of command line argument here
    NUM_SYMBOLS = 4000
    NUM_SYMBOLS_DISPLAY = 7

    monitor = Monitor(NUM_SYMBOLS)
    monitor.run()

    while True:
        try:
            raw_data = monitor.get_data(NUM_SYMBOLS_DISPLAY)
            table_data = [[data['token_info']['name'], data['token_info']['symbol'], *data['price_data'][:6]] for data in raw_data.values()]

            table = tabulate(table_data, headers=["Name", "Symbol", "2hr change", "6hr change", "12hr change", "24hr change", "48hr change", "Recent price"])
            print(table)
            print()

            sleep(60 * 10)
        
        except KeyboardInterrupt:
            break
    
    monitor.stop()

if __name__ == "__main__":
    main()