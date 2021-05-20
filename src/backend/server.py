from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os
import atexit
from screener.monitor import Monitor

DEV = "DYNO" not in os.environ

if DEV:
    SYMBOLS_TO_MONITOR = 500
    PAGE_SIZE = 50

else:
    SYMBOLS_TO_MONITOR = 6000
    PAGE_SIZE = 50

monitor = Monitor(SYMBOLS_TO_MONITOR, PAGE_SIZE)
monitor.run()

app = Flask(__name__)
cors = CORS(app)

@app.route("/api/get_pages_info", methods=['GET'], strict_slashes=False)
@cross_origin()
def get_pages_info():
    page_min, page_max, page_size, num_symbols = monitor.get_page_request_info() 

    return jsonify({'pageMin': page_min, 'pageMax': page_max, 'pageSize': page_size, 'numSymbols': num_symbols}), 200

@app.route("/api/get_page_data", methods=['POST'], strict_slashes=False)
@cross_origin()
def get_page():
    form_json = request.json

    page_number = int(form_json['pageNumber'])
    reverse = form_json['reverse']

    data = monitor.get_page_data(page_number, reverse=reverse)

    return jsonify(data), 200

if __name__ == "__main__":
    atexit.register(monitor.stop)
    app.run(debug=DEV)