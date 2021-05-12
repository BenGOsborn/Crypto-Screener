from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os
import traceback
from screener.monitor import Monitor

SYMBOLS_TO_MONITOR = 6000
RETURN_SYMBOLS = 50
PAGE_MIN = 1
PAGE_MAX = (SYMBOLS_TO_MONITOR - 1) // RETURN_SYMBOLS # This is confusing

monitor = Monitor(SYMBOLS_TO_MONITOR)
monitor.run()

app = Flask(__name__)
cors = CORS(app)

# I need another router for determining how many pages there should be
@app.route("/api/get_pages_info", methods=['GET'], strict_slashes=False)
@cross_origin()
def get_pages_info():
    return jsonify({'page_min': PAGE_MIN, 'page_max': PAGE_MAX}), 200

@app.route("/api/get_page", methods=['POST'], strict_slashes=False)
@cross_origin()
def get_page():
    try:
        form_json = request.json

        page_number = int(form_json['page_number'])
        if page_number < PAGE_MIN or page_number > PAGE_MAX:
            raise ValueError("Invalid page number")
        reverse = form_json['reverse']

        start_index = (page_number - 1) * RETURN_SYMBOLS
        end_index = page_number * RETURN_SYMBOLS

        data = monitor.get_data(start_index, end_index, reverse=reverse)

        return jsonify(data), 200

    except:
        err = traceback.format_exc()
        print(err)
        return jsonify({'error': err}), 400

if __name__ == "__main__":
    app.run(debug=("DYNO" not in os.environ))