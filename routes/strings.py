from flask import Blueprint, request, jsonify
from utils.analyzer import analyze_string
from config import db
from datetime import datetime
from utils.query_parser import (
    parse_natural_language_query,
    QueryParsingError,
    ConflictingFiltersError,
)

strings_bp = Blueprint('strings', __name__)

def _document_to_response(document):
    return {
        "id": document["_id"],
        "value": document["value"],
        "properties": document["analysis"],
        "created_at": document["created_at"],
    }

def _build_query_from_filters(filters):
    mongo_query = {}
    if "is_palindrome" in filters:
        mongo_query["analysis.is_palindrome"] = filters["is_palindrome"]
    if "word_count" in filters:
        mongo_query["analysis.word_count"] = filters["word_count"]
    if "min_length" in filters or "max_length" in filters:
        length_conditions = {}
        if "min_length" in filters:
            length_conditions["$gte"] = filters["min_length"]
        if "max_length" in filters:
            length_conditions["$lte"] = filters["max_length"]
        mongo_query["analysis.length"] = length_conditions
    if "contains_character" in filters:
        character = filters["contains_character"]
        mongo_query[f"analysis.character_frequency_map.{character}"] = {"$exists": True}
    return mongo_query

@strings_bp.route('/strings', methods=['POST'])
def create_string():
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({"error": "Missing 'value' in request body"}), 400
    
    value = data['value']
    if not isinstance(value, str):
        return jsonify({"error": "'value' must be a string"}), 422
    
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

@strings_bp.route('/strings', methods=['GET'])
def list_strings():
    filters = {}
    raw_is_palindrome = request.args.get('is_palindrome')
    if raw_is_palindrome is not None:
        normalized = raw_is_palindrome.lower()
        if normalized not in ('true', 'false'):
            return jsonify({"error": "Invalid value for 'is_palindrome'. Use true or false."}), 400
        filters['is_palindrome'] = normalized == 'true'

    raw_min_length = request.args.get('min_length')
    if raw_min_length is not None:
        try:
            filters['min_length'] = int(raw_min_length)
        except ValueError:
            return jsonify({"error": "Invalid value for 'min_length'. Must be an integer."}), 400

    raw_max_length = request.args.get('max_length')
    if raw_max_length is not None:
        try:
            filters['max_length'] = int(raw_max_length)
        except ValueError:
            return jsonify({"error": "Invalid value for 'max_length'. Must be an integer."}), 400

    if 'min_length' in filters and filters['min_length'] < 0:
        return jsonify({"error": "'min_length' must be non-negative."}), 400
    if 'max_length' in filters and filters['max_length'] < 0:
        return jsonify({"error": "'max_length' must be non-negative."}), 400
    if 'min_length' in filters and 'max_length' in filters and filters['min_length'] > filters['max_length']:
        return jsonify({"error": "'min_length' cannot be greater than 'max_length'."}), 400

    raw_word_count = request.args.get('word_count')
    if raw_word_count is not None:
        try:
            word_count = int(raw_word_count)
        except ValueError:
            return jsonify({"error": "Invalid value for 'word_count'. Must be an integer."}), 400
        if word_count < 0:
            return jsonify({"error": "'word_count' must be non-negative."}), 400
        filters['word_count'] = word_count

    contains_character = request.args.get('contains_character')
    if contains_character is not None:
        if len(contains_character) != 1:
            return jsonify({"error": "'contains_character' must be a single character."}), 400
        filters['contains_character'] = contains_character

    mongo_query = _build_query_from_filters(filters)
    documents = list(db.strings.find(mongo_query))
    data = [_document_to_response(doc) for doc in documents]

    return jsonify({
        "data": data,
        "count": len(data),
        "filters_applied": filters
    }), 200

@strings_bp.route('/strings/filter-by-natural-language', methods=['GET'])
def filter_strings_by_natural_language():
    query = request.args.get('query', '')
    try:
        parsed_filters = parse_natural_language_query(query)
    except ConflictingFiltersError as exc:
        return jsonify({"error": str(exc)}), 422
    except QueryParsingError as exc:
        return jsonify({"error": str(exc)}), 400

    mongo_query = _build_query_from_filters(parsed_filters)
    documents = list(db.strings.find(mongo_query))
    data = [_document_to_response(doc) for doc in documents]

    return jsonify({
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }), 200

@strings_bp.route('/strings/<path:string_value>', methods=['GET'])
def get_string(string_value):
    document = db.strings.find_one({"value": string_value})
    if not document:
        return jsonify({"error": "String does not exist in the system"}), 404
    return jsonify(_document_to_response(document)), 200

@strings_bp.route('/strings/<path:string_value>', methods=['DELETE'])
def delete_string(string_value):
    result = db.strings.delete_one({"value": string_value})
    if result.deleted_count == 0:
        return jsonify({"error": "String does not exist in the system"}), 404
    return '', 204