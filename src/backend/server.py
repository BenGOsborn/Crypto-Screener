from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os
from screener.tokens_monitor import TokensMonitor
from dotenv import load_dotenv

# Heroku environment contains "DYNO" - if there is a "DYNO" it must be heroku, if not must be dev
DEV = "DYNO" not in os.environ

# Initialize the symbols and page sizes for dev mode and deployment mode
if DEV:
    # Load environment variables
    load_dotenv()

    SYMBOLS_TO_MONITOR = 20
    PAGE_SIZE = 5

else:
    SYMBOLS_TO_MONITOR = 4000
    PAGE_SIZE = 50

# Initialize the token monitor
monitor = TokensMonitor(SYMBOLS_TO_MONITOR, PAGE_SIZE)
monitor.monitor()

# Create the flask app and enable CORS
app = Flask(__name__)
cors = CORS(app)


@ app.route("/api/get_pages_info", methods=['GET'], strict_slashes=False)
@ cross_origin()
def get_pages_info():
    # Get the information about what can be requested to the server
    page_min, page_max, page_size, num_symbols = monitor.get_page_request_info()

    return jsonify({'pageMin': page_min, 'pageMax': page_max, 'pageSize': page_size, 'numSymbols': num_symbols}), 200


@ app.route("/api/get_page_data", methods=['POST'], strict_slashes=False)
@ cross_origin()
def get_page():
    # Get the token information from the specified page
    form_json = request.json

    page_number = int(form_json['pageNumber'])
    reverse = form_json['reverse']

    #  Also, I need to check this to make sure that it is not empty
    data = monitor.get_page_data(page_number, reverse=reverse)
    assert len(data) > 0, "No data available!"

    return jsonify(data), 200


# Start the server in the correct mode and declare the exit cleanup
if __name__ == "__main__":
    app.run(debug=DEV, host="0.0.0.0", port=os.getenv("PORT", 5000))
