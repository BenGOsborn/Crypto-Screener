from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os
from screener.monitor import Monitor

# I also need flask cors

NUM_SYMBOLS = 4000

app = Flask(__name__)
cors = CORS(app)

@app.route("/api/get_cryptos")
@cross_origin()
def get_cryptos():
    pass

if __name__ == "__main__":
    app.run(debug=("DYNO" not in os.environ))