from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os
import traceback
from screener.monitor import Monitor

NUM_SYMBOLS = 6000

monitor = Monitor(NUM_SYMBOLS)
monitor.run()

app = Flask(__name__)
cors = CORS(app)

@app.route("/api/get_cryptos", methods=['POST'], strict_slashes=False)
@cross_origin()
def get_cryptos():
    try:
        form_json = request.json

        num_symbols = form_json['num_symbols']
        reverse = form_json['reverse']

        data = monitor.get_data(num_symbols, reverse=reverse)

        return jsonify(data), 200

    except:
        pass # Do something with the error

if __name__ == "__main__":
    app.run(debug=("DYNO" not in os.environ))