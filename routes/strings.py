from flask import Blueprint
from utils.analyzer import analyze_string

strings_bp = Blueprint('strings', __name__)