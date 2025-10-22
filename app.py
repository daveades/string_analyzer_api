from flask import Flask, jsonify
from config import db


app = Flask(__name__)

@app.route('/', methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the String Analyzer API!"}), 200


if __name__ == '__main__':
    app.run(debug=True)
