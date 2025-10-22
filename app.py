from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]


@app.route('/', methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the String Analyzer API!"}), 200

@app.route('/test-db', methods=["GET"])
def test_db():
    try:
        db.command("ping")
        return jsonify({"message": "Database connection successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
