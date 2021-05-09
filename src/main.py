import numpy as np
from api import API

# Now I also need some sort of threading function which can run through them synonomously and get the best ones?

def main():
    api = API()

    price_data = api.get_price_data("dogecoin")
    score = moon_score(price_data)

    print(score)

if __name__ == "__main__":
    main()