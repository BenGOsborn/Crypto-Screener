import numpy as np
from api import API

# Now I also need some sort of threading function which can run through them synonomously and get the best ones?

def moon_score(price_data, n_steps=5):
    price_rate_1 = price_data[1:] / price_data[:-1]
    price_rate_1_rate = price_rate_1[1:] / price_rate_1[:-1]

    N_STEPS = n_steps
    price_rate_n = price_data[N_STEPS:] / price_data[:-N_STEPS]
    price_rate_n_rate = price_rate_n[N_STEPS:] / price_rate_n[:-N_STEPS]

    slope_1 = price_rate_1[-1]
    concavity_1 = price_rate_1_rate[-1]
    slope_n = price_rate_n[-1]
    concavity_n = price_rate_n_rate[-1]

    score = (slope_1 ** ((1 - (1 / np.math.sqrt(n_steps))) * concavity_1)) * (slope_n ** ((1 / np.math.sqrt(n_steps)) * concavity_n))

    ret_dict = {"slope_1": slope_1, "concavity_1": concavity_1, "slope_n": slope_n, "concavity_n": concavity_n, "moon_score": score}

    return ret_dict

def main():
    api = API()

    price_data = api.get_price_data("dogecoin")
    score = moon_score(price_data)

    print(score)

if __name__ == "__main__":
    main()