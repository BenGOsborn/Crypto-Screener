import numpy as np

class TokenMath:
    """
    A collection of math functions for the tokens
    """

    @staticmethod
    def exp_moving_average(data, window):
        """
        Calculates an exponential moving average of the given time series data over the specified window

        :param data A numpy array containing the time series data to calculate the moving average over
        :param window A number which represents the time period to calculate the moving average over

        :return The exponential moving average of the given data over the given window
        """
        kernel = np.exp(np.linspace(-1, 0, window))
        kernel /= kernel.sum()

        return np.convolve(data, kernel, mode='valid')

    @staticmethod
    def unusual_value(distribution, test_value):
        """
        Determines the probability of the values below the test value occuring for the distribution

        :param distribution A numpy array containing the distribution to compare against
        :param test_value A numerical value to test against the distribution

        :return A number that represents the probability of the elements below the test value occuring
        """
        mean = np.mean(distribution)
        std = np.std(distribution)

        distribution = np.random.normal(loc=mean, scale=std, size=10000)
        p_value = np.sum(distribution < test_value) / float(len(distribution))

        return p_value

    @staticmethod
    def custom_log(x, base):
        """
        A custom logarithmic function that instead of trailing to negative infinity trails to 0

        :param x The number to apply the function to
        :param base A number that represents the base of the logarithm

        :return A number which represents the value with the custom log function applied
        """
        a = ((1 / np.math.log(base)) - 1) / (base ** 2)
        b = (2 - (1 / np.math.log(base))) / base

        return np.math.log(x, base) if x >= base else a * (x ** 2) + b * x

    @staticmethod
    def parse_token_data(token_history):
        """
        Parses the token history data and extracts the price changes, prices, volumes, and a ranking of the token

        :param token_history A numpy array containing the price history and the volume history of the token in hours 

        :return An array which contains the percentage price changes over the past 2 hours, 6 hours, 12 hours, 24 hours, and 48 hours, as well as the recent price of the token, the recent 24h volume of the token, and a moon score ranking which is used to rank tokens - the higher the score the better the token
        """
        EPSILON = 1e-6
        WINDOW = 12

        price_data = token_history[0]
        volume_data = token_history[1]

        recent_price = price_data[-1]
        recent_volume = volume_data[-1]

        CHANGE_PERIODS = [2, 6, 12, 24, 48] # 2 hour change, 6 hour change, 12 hour change, 24 hour change, 48 hour change
        moving_price_changes = [(TokenMath.exp_moving_average(price_data, WINDOW)[period:] / (TokenMath.exp_moving_average(price_data, WINDOW)[:-period] + EPSILON))[-1] for period in CHANGE_PERIODS]

        # ---------------------------- Moon Score calculations -----------------------------------------

        moon_score = (TokenMath.custom_log(np.mean(volume_data[-CHANGE_PERIODS[0]:]), 1e+6) # This is the base volume it is at
                     * TokenMath.unusual_value(volume_data[-CHANGE_PERIODS[-1]:-CHANGE_PERIODS[0]], np.mean(volume_data[-CHANGE_PERIODS[0]:]))) # This is the amount larger than its previous data

        exp_sum = np.sum([np.math.exp(np.sqrt(x)) for x in CHANGE_PERIODS])

        temp_moon_score = 1
        for moving_price_change, reversed_change_period in zip(moving_price_changes, CHANGE_PERIODS[::-1]):
            partial_price = moving_price_change * np.math.exp(np.math.sqrt(reversed_change_period)) / exp_sum
            temp_moon_score *= partial_price
        
        moon_score *= TokenMath.custom_log(temp_moon_score, np.math.e)

        # ---------------------------- End of Moon Score calculations -----------------------------------------

        price_changes = [((price_data[period:] / (price_data[:-period] + EPSILON))[-1] - 1) * 100 for period in CHANGE_PERIODS]
        
        return price_changes + [recent_price, recent_volume, moon_score]