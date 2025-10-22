from flask import Flask, jsonify
from routes.strings import strings_bp
from config import db


app = Flask(__name__)

app.register_blueprint(strings_bp)

@app.route('/', methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the String Analyzer API!"}), 200


if __name__ == '__main__':
    app.run(debug=True)
