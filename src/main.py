import numpy as np
from api import API

# Now I also need some sort of threading function which can run through them synonomously and get the best ones?

def moon_score(price_data):
    price_rate_1 = price_data[1:] / price_data[:-1]
    price_rate_1_rate = price_rate_1[1:] / price_rate_1[:-1]

    N_STEPS = 5
    price_rate_n = price_data[N_STEPS:] / price_data[:-N_STEPS]
    price_rate_n_rate = price_rate_n[N_STEPS:] / price_rate_n[:-N_STEPS]

    slope_1 = price_rate_1[-1]
    concavity_1 = price_rate_1_rate[-1]
    slope_n = price_rate_n[-1]
    concavity_n = price_rate_n_rate[-1]

    score = (slope_1 ** (0.4 * concavity_1)) * (slope_n ** (0.6 * concavity_n))

    print(f"slope_1: {slope_1}\nconcavity_1: {concavity_1}\nslope_n: {slope_n}\nconcavity_n: {concavity_n}\nscore: {score}")

    return score

def main():
    api = API()

    price_data = api.get_price_data("bitcoin")
    score = moon_score(price_data)

if __name__ == "__main__":
    main()