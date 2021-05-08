import numpy as np
from api import API

# Now I also need some sort of threading function which can run through them synonomously and get the best ones?

def moving_average(array, window):
    mv_avg = np.convolve(array, np.ones(window), mode='valid') / window

    return mv_avg

# Maybe it is just a better idea to rank by percent change over 10 minutes or something ??????????
def preprocess(price_data):
    WINDOW = 30 # Play with this

    price_data_spliced = price_data[-60:] # For the purpose of visualizing the data

    # Maybe instead do a moving average of the slopes?

    minute_percent_change = 100 * (price_data_spliced[1:] - price_data_spliced[:-1]) / price_data_spliced[:-1]
    mv_avg = moving_average(price_data_spliced, WINDOW)

    percent_price_change = 100 * (mv_avg[1:] - mv_avg[:-1]) / mv_avg[:-1] # Derivative
    percent_slope_change = 100 * (percent_price_change[1:] - percent_price_change[:-1]) / percent_price_change[:-1] # Concavity

    # How can I make some sort of score from these?
    return minute_percent_change[-1], percent_price_change[-1], percent_slope_change[-1]

def main():
    api = API()

    price_data = api.get_price_data("bitcoin")

    print(preprocess(price_data))

if __name__ == "__main__":
    main()