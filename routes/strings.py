from flask import Blueprint, request, jsonify
from utils.analyzer import analyze_string
from config import db
from datetime import datetime

strings_bp = Blueprint('strings', __name__)

@strings_bp.route('/strings', methods=['POST'])
def create_string():
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({"error": "Missing 'value' in request body"}), 400
    
    value = data['value']
    if not isinstance(value, str):
        return jsonify({"error": "'value' must be a string"}), 400
    
    analysis = analyze_string(value)
    sha256_hash = analysis['sha256_hash']

    if db.strings.find_one({"_id": sha256_hash}):
        return jsonify({"error": "String already exists"}), 409
    
    string_data = {
        "_id": sha256_hash,
        "value": value,
        "analysis": analysis,
        "created_at": datetime.utcnow().isoformat() + 'Z'
    }
    db.strings.insert_one(string_data)

    return jsonify({
        "id": sha256_hash,
        "value": value,
        "properties": analysis,
        "created_at": string_data["created_at"]
    }), 201