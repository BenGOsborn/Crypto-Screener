# [CryptoScreener](https://crypto-screener.netlify.app/)

## A web app that screens cryptocurrency API data from CoinGecko to rank them in terms of the ones that are performing the best most currently.

### How it was built

The frontend of the app was built using ReactJS and NextJS which allowed me to create a static single page site with full SEO support. The frontend was set up to continuously deploy to Netlify whenever a commit is pushed to the main branch.

The backend of the app was built using Python and Flask. The backend spawns a daemon thread which continuously calls the cryptocurrency data from the CoinGecko API and then performs an operation on this data to give the cryptocurrency token a score which is used to determine how well it is performing relative to others - the higher the score, the better it is performing. The mathematics behind how these tokens are scored is explained below. The Flask app reads the data crunched by the screener and returns a list of tokens to the client who made the request however the client specified. The backend is set up to continuously deploy to Heroku whenever a commit is pushed to the main branch.

The rankings for the tokens are stored in a Redis cache and are set to expire after a given amount of time. New data will not be fetched for each token if it is present within Redis. Each instance of the server randomly shuffles its list of tokens before attempting to fetch the data for them, so that each instance of the server is updating the data for different tokens and so that there is little overlap. Redis also allows each server to share the same data between them, making sure that no matter what server is hit, the data returned will be consistent with the others and thus prevents redundency by preventing the need for each server to be entirely dependent on itself for keeping a record of the data which also saves resources being spent to update the data.

### Token screening math

The math behind ranking the tokens uses a concept I call a "moon score", which gets its name from popular cryptocurrencies being referred to as "going to the moon". The higher the moon score, the better performing the token. The moon score consists of 3 different parts based on the volume, the volume change, and the price changes which are all multipled together and parsed through a modified logarithm (as defined below) to get the final result.

The volume part is determined based on a modified logarithm that instead of going to -infinity instead goes to 0. This provides a nice way of scaling down the volume, where large volume values are all relatively the same and dont affect the rest of the score much, but low volume values drastically lower the score.

The volume change part looks at the previous volume changes and creates a distribution from them which is then used to determine the probability of getting a value less than the one specified. This way, higher volume changes create a greater probability and don't modify the score as much, compared to regular changes which decrease the score.

Finally the price changes part uses exponential moving averages over different time periods: 2 hours, 6 hours, 12 hours, 24 hours, and 48 hours. The most recent price increase for each time period is weighted exponentially based on its time period, and then multipled together with the others to get the final result for this part.
