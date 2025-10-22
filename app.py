import os
from flask import Flask, jsonify
from routes.strings import strings_bp
from config import db

app = Flask(__name__)

app.register_blueprint(strings_bp)

app.json.sort_keys = False
app.json.compact = False

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG") == "1"
    app.run(debug=debug_mode)
