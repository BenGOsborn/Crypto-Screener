import numpy as np
from api import API
import matplotlib.pyplot as plt

# Now I also need some sort of threading function which can run through them synonomously and get the best ones?

def moving_average(array, window):
    mv_avg = np.convolve(array, np.ones(window), mode='valid') / window

    return mv_avg

def preprocess(price_data):
    WINDOW = 15

    minute_percent_change = 100 * (price_data[1:] - price_data[:-1]) / price_data[:-1]
    mv_avg = moving_average(price_data, WINDOW)

    percent_price_change = 100 * (mv_avg[1:] - mv_avg[:-1]) / mv_avg[:-1] # Derivative
    percent_slope_change = 100 * (percent_price_change[1:] - percent_price_change[:-1]) / percent_price_change[:-1] # Concavity

    plt.plot(price_data)
    plt.show()

    # How can I make some sort of score from these?
    return minute_percent_change[-1], percent_price_change[-1], percent_slope_change[-1]

def main():
    api = API()

    price_data = api.get_price_data("bitcoin") # Be careful - this plot looks different than the one at https://www.coingecko.com/en/coins/bitcoin for some reason ????

    print(preprocess(price_data))

if __name__ == "__main__":
    main()