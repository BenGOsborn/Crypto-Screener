from screener.monitor import Monitor
from time import sleep
from tabulate import tabulate
import atexit

NUM_SYMBOLS = 5000
PAGE_SIZE = 50

monitor = Monitor(NUM_SYMBOLS, PAGE_SIZE)
monitor.run()

def main(): # Maybe some sort of command line argument here
    while True:
        try:
            raw_data = monitor.get_page_data(1, reverse=False)

            table = tabulate(raw_data)
            print(table)
            print()

            sleep(10)
        
        except KeyboardInterrupt:
            break
    
    monitor.stop()

if __name__ == "__main__":
    atexit.register(monitor.stop)
    main()


