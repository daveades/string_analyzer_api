import hashlib
from collections import Counter

def analyze_string(s):
    s_cleaned = s.strip()
    length = len(s_cleaned)
    is_palindrome = s_cleaned.lower() == s_cleaned[::-1].lower()
    unique_chars = len(set(s_cleaned))
    word_count = len(s_cleaned.split())
    sha256_hash = hashlib.sha256(s_cleaned.encode()).hexdigest()
    char_frequency_map = dict(Counter(s_cleaned))

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_chars,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": char_frequency_map
    }