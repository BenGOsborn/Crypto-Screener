from screener.api import API
from screener.tokens_monitor import TokensMonitor

if __name__ == "__main__":
    api = API()

    history = api.get_token_history("bitcoin")

    volume_data = history[1]
    print(volume_data.shape)
    
    parsed = TokensMonitor.parse_token_data(history)

    print(parsed)