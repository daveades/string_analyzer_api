import re

class QueryParsingError(Exception):
    """Raised when a natural language query cannot be interpreted into filters."""
    pass

class ConflictingFiltersError(QueryParsingError):
    """Raised when a natural language query produces conflicting filters."""
    pass

def _set_filter(filters: dict, key: str, value):
    if key in filters and filters[key] != value:
        raise ConflictingFiltersError(f"Conflicting constraint detected for '{key}'.")
    filters[key] = value

def parse_natural_language_query(query: str) -> dict:
    if not query or not query.strip():
        raise QueryParsingError("Query must not be empty.")
    
    text = query.strip().lower()
    filters: dict = {}

    if any(word in text for word in ("palindromic", "palindrome")):
        _set_filter(filters, "is_palindrome", True)

    if "non-palindromic" in text or "not palindromic" in text:
        _set_filter(filters, "is_palindrome", False)

    if any(phrase in text for phrase in ("single word", "one word")):
        _set_filter(filters, "word_count", 1)

    longer_match = re.search(r"(?:longer|greater) than (\d+)", text)
    if longer_match:
        threshold = int(longer_match.group(1)) + 1
        _set_filter(filters, "min_length", threshold)

    at_least_match = re.search(r"(?:at least|minimum of) (\d+)", text)
    if at_least_match:
        threshold = int(at_least_match.group(1))
        _set_filter(filters, "min_length", threshold)

    shorter_match = re.search(r"(?:shorter|less) than (\d+)", text)
    if shorter_match:
        threshold = int(shorter_match.group(1)) - 1
        if threshold < 0:
            threshold = 0
        _set_filter(filters, "max_length", threshold)

    at_most_match = re.search(r"(?:at most|max(?:imum)? of) (\d+)", text)
    if at_most_match:
        threshold = int(at_most_match.group(1))
        _set_filter(filters, "max_length", threshold)

    if "first vowel" in text:
        _set_filter(filters, "contains_character", "a")

    char_match = re.search(r"contain(?:ing)?(?: the letter)? ([a-z])", text)
    if char_match:
        _set_filter(filters, "contains_character", char_match.group(1))

    if not filters:
        raise QueryParsingError("Unable to parse natural language query into filters.")

    if (
        "min_length" in filters
        and "max_length" in filters
        and filters["min_length"] > filters["max_length"]
    ):
        raise ConflictingFiltersError("Length constraints are conflicting.")
    
    return filters