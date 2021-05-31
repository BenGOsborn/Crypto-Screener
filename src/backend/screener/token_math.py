import numpy as np

class TokenMath:
    """
    A collection of math functions for tokens
    """

    @staticmethod
    def significant_figures(number, sig_figs):
        """
        Rounds a number to the specified number of significant figures

        :param number The number to round
        :param The number of significant figures

        :return The number rounded to the given number of significant figures
        """
        return round(number, sig_figs - int(np.math.floor(np.math.log10(abs(number)))) - 1)

    @staticmethod
    def exp_moving_average(data, window):
        """
        Calculates an exponential moving average of the given time series data over the specified window

        :param data The time series data to calculate the moving average over
        :param window The time period to calculate the moving average over

        :return The exponential moving average of the given data over the given window
        """
        kernel = np.exp(np.linspace(-1, 0, window))
        kernel /= kernel.sum()

        return np.convolve(data, kernel, mode='valid')

    @staticmethod
    def unusual_value(distribution, test_value):
        """
        Determines the probability of the values below the test value occuring for the distribution

        :param distribution Distribution to compare against
        :param test_value Value to test against the distribution

        :return The probability of the elements below the test value occuring
        """
        mean = np.mean(distribution)
        std = np.std(distribution)

        distribution = np.random.normal(loc=mean, scale=std, size=10000)
        p_value = np.sum(distribution < test_value) / float(len(distribution))

        return p_value

    @staticmethod
    def custom_log(x, base):
        a = ((1 / np.math.log(base)) - 1) / (base ** 2)
        b = (2 - (1 / np.math.log(base))) / base

        return np.math.log(x, base) if x >= base else a * (x ** 2) + b * x

    @staticmethod
    def parse_token_data(token_history):
        EPSILON = 1e-6
        WINDOW = 12
        DECIMALS = 4

        price_data = token_history[0]
        volume_data = token_history[1]

        recent_price = TokenMath.significant_figures(price_data[-1], DECIMALS) if price_data[-1] < 1 else round(price_data[-1], DECIMALS)
        recent_volume = TokenMath.significant_figures(volume_data[-1], DECIMALS) if volume_data[-1] < 1 else round(volume_data[-1], DECIMALS)

        CHANGE_PERIODS = [2, 6, 12, 24, 48] # 2 hour change, 6 hour change, 12 hour change, 24 hour change, 48 hour change
        moving_price_changes = [(TokenMath.exp_moving_average(price_data, WINDOW)[period:] / (TokenMath.exp_moving_average(price_data, WINDOW)[:-period] + EPSILON))[-1] for period in CHANGE_PERIODS]

        # ---------------------------- Moon Score calculations -----------------------------------------

        moon_score = (TokenMath.custom_log(np.mean(volume_data[-CHANGE_PERIODS[0]:]), 1e+6) # This is the base volume it is at
                     * TokenMath.unusual_value(volume_data[-CHANGE_PERIODS[-1]:-CHANGE_PERIODS[0]], np.mean(volume_data[-CHANGE_PERIODS[0]:]))) # This is the amount larger than its previous data

        temp_moon_score = 1
        for moving_price_change, reversed_change_period in zip(moving_price_changes, CHANGE_PERIODS[::-1]):
            partial_price = (moving_price_change ** np.math.sqrt(reversed_change_period)) # I want some way of normalizing this ?

            temp_moon_score *= partial_price
        
        moon_score *= TokenMath.custom_log(temp_moon_score, np.math.e)

        # ---------------------------- End of Moon Score calculations -----------------------------------------

        price_changes = [TokenMath.significant_figures(((price_data[period:] / (price_data[:-period] + EPSILON))[-1] - 1) * 100, DECIMALS) for period in CHANGE_PERIODS]
        
        return price_changes + [recent_price, recent_volume, moon_score]