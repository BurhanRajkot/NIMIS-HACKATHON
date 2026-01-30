"""
Address Normalizer Module for Indian Addresses.

Provides modular functions for cleaning, expanding, and extracting
structured components from messy Indian address text.

Functions:
    - clean_text(): Basic text cleaning (lowercase, punctuation, whitespace)
    - expand_abbreviations(): Expand common Indian address abbreviations
    - correct_spelling(): Lightweight spell correction using fuzzy matching
    - extract_address_components(): Extract landmarks, directions, street info

Returns structured output with clean_text, landmarks, directions, street_info.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


# =============================================================================
# ABBREVIATION MAPPINGS
# =============================================================================

# Common Indian address abbreviations and their expansions
ABBREVIATION_MAP = {
    # Road/Street types
    "rd": "road",
    "st": "street",
    "ln": "lane",
    "ave": "avenue",
    "blvd": "boulevard",
    
    # Hindi/Regional transliterations
    "gali": "lane",
    "gully": "lane",
    "marg": "road",
    "path": "road",
    "sadak": "road",
    "nagr": "nagar",
    "ngr": "nagar",
    "chowk": "square",
    "chawk": "square",
    "chauk": "square",
    "mohalla": "locality",
    "mohala": "locality",
    "peth": "area",
    "wadi": "colony",
    "nagar": "nagar",  # Keep as-is but ensure consistency
    "puram": "puram",
    "puri": "puri",
    "vihar": "vihar",
    "encl": "enclave",
    "extn": "extension",
    "ext": "extension",
    
    # Building types
    "bldg": "building",
    "blk": "block",
    "flr": "floor",
    "fl": "floor",
    "apt": "apartment",
    "appt": "apartment",
    "flt": "flat",
    "hse": "house",
    "hno": "house number",
    "h.no": "house number",
    "plt": "plot",
    
    # Positional
    "nr": "near",
    "opp": "opposite",
    "adj": "adjacent",
    "bhnd": "behind",
    "bh": "behind",
    "b/h": "behind",
    "nxt": "next to",
    
    # Areas/Admin
    "sec": "sector",
    "ph": "phase",
    "dist": "district",
    "div": "division",
    "tq": "taluk",
    "tal": "taluk",
    
    # Common shortcuts
    "mkt": "market",
    "stn": "station",
    "rly": "railway",
    "hosp": "hospital",
    "govt": "government",
    "pvt": "private",
    "soc": "society",
    "chs": "cooperative housing society",
    "po": "post office",
    "ps": "police station",
}


# =============================================================================
# SPELL CORRECTION DICTIONARY
# =============================================================================

# Common address words with correct spellings
# Maps common misspellings/variations to canonical form
SPELLING_DICTIONARY = {
    # Correctly spelled canonical words
    "road", "street", "lane", "nagar", "colony", "market", "hospital",
    "temple", "mosque", "church", "school", "college", "station",
    "railway", "metro", "airport", "bridge", "flyover", "signal",
    "square", "circle", "garden", "park", "building", "apartment",
    "floor", "block", "sector", "phase", "society", "complex",
    "tower", "plaza", "mall", "bazaar", "chowk", "crossing",
    "junction", "opposite", "near", "behind", "beside", "adjacent",
    "north", "south", "east", "west", "main", "old", "new",
    "first", "second", "third", "fourth", "fifth",
    "municipal", "corporation", "office", "court", "police",
    "post", "bank", "hotel", "lodge", "restaurant", "shop",
    "store", "showroom", "petrol", "pump", "bus", "stand", "stop",
}

# Common misspellings mapped to correct form
MISSPELLING_MAP = {
    "raod": "road",
    "stret": "street",
    "streat": "street",
    "lain": "lane",
    "naagr": "nagar",
    "nagaar": "nagar",
    "colny": "colony",
    "colonny": "colony",
    "markt": "market",
    "hosptal": "hospital",
    "hospitl": "hospital",
    "templ": "temple",
    "templa": "temple",
    "scool": "school",
    "schol": "school",
    "staion": "station",
    "staton": "station",
    "railwy": "railway",
    "bridg": "bridge",
    "sqare": "square",
    "squar": "square",
    "gardne": "garden",
    "gardn": "garden",
    "bildng": "building",
    "bilding": "building",
    "apartmnt": "apartment",
    "socity": "society",
    "opposit": "opposite",
    "opsite": "opposite",
    "behnd": "behind",
    "behid": "behind",
    "nrth": "north",
    "soth": "south",
    "esat": "east",
    "wset": "west",
}


# =============================================================================
# PATTERN DEFINITIONS
# =============================================================================

# Direction/positional words that indicate landmark references
DIRECTION_WORDS = [
    "near", "behind", "opposite", "beside", "adjacent", "next to",
    "in front of", "across from", "after", "before", "facing",
    "towards", "beyond", "past", "above", "below", "inside", "outside",
]

# Pattern to match landmark phrases like "near X", "behind Y"
LANDMARK_PHRASE_PATTERN = re.compile(
    r'\b(near|behind|opposite|beside|adjacent to|next to|in front of|across from|after|before|facing)\s+([^,\n]+?)(?=[,\n]|$)',
    re.IGNORECASE
)

# Pattern to match street/lane numbers like "1st lane", "2nd gali", "lane no 5"
STREET_NUMBER_PATTERN = re.compile(
    r'\b(\d+)(?:st|nd|rd|th)?\s*(lane|gali|gully|street|road|cross|main)\b|\b(lane|gali|gully|street|road)\s*(?:no\.?|number)?\s*(\d+)\b',
    re.IGNORECASE
)

# Pattern to match building/floor numbers
BUILDING_NUMBER_PATTERN = re.compile(
    r'\b(?:flat|apartment|apt|floor|flr|block|blk|plot|house|hno|h\.no)\s*(?:no\.?|number)?\s*[:\-]?\s*(\d+[a-z]?)\b',
    re.IGNORECASE
)


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def clean_text(text: str) -> str:
    """
    Clean raw address text with basic normalization.
    
    Operations:
    1. Unicode normalization (handles Devanagari, Tamil, etc.)
    2. Lowercase conversion
    3. Remove extra whitespace
    4. Remove excessive punctuation (keep meaningful ones)
    
    Args:
        text: Raw address string
        
    Returns:
        Cleaned text string
        
    ML Note: Basic cleaning is essential preprocessing for any NLP task.
    We preserve some punctuation (commas, hyphens) as they carry structural
    meaning in addresses.
    """
    if not text:
        return ""
    
    # Step 1: Unicode normalization (NFKC handles compatibility characters)
    text = unicodedata.normalize("NFKC", text)
    
    # Step 2: Lowercase for consistent matching
    text = text.lower()
    
    # Step 3: Normalize special characters
    # Replace multiple spaces, tabs, newlines with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Step 4: Clean punctuation
    # Remove duplicate punctuation (keep single instance)
    text = re.sub(r'([,.\-:;])\1+', r'\1', text)
    
    # Remove punctuation at start/end of words (but keep between)
    text = re.sub(r'\s[,.\-:;]+\s', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove leading/trailing punctuation
    text = text.strip('.,;:-')
    
    return text


def expand_abbreviations(text: str, custom_map: Dict[str, str] = None) -> str:
    """
    Expand common Indian address abbreviations.
    
    Handles abbreviations like:
    - rd → road, st → street
    - nagr → nagar, gali → lane
    - nr → near, opp → opposite
    
    Args:
        text: Address text (should be cleaned first)
        custom_map: Optional additional abbreviation mappings
        
    Returns:
        Text with abbreviations expanded
        
    ML Note: Expansion before matching improves recall since patterns
    only need to match canonical forms. We use word boundaries to avoid
    partial replacements (e.g., "standard" shouldn't become "standardard").
    """
    if not text:
        return ""
    
    # Merge custom mappings with defaults
    abbrev_map = ABBREVIATION_MAP.copy()
    if custom_map:
        abbrev_map.update(custom_map)
    
    # Sort by length descending to match longer abbreviations first
    # This prevents "b/h" from being partially matched before "bh"
    sorted_abbrevs = sorted(abbrev_map.keys(), key=len, reverse=True)
    
    result = text
    for abbrev in sorted_abbrevs:
        expansion = abbrev_map[abbrev]
        
        # Use word boundaries, handle periods in abbreviations
        # Escape special regex characters in abbreviation
        escaped = re.escape(abbrev)
        
        # Match with optional trailing period (common in abbreviations)
        pattern = rf'\b{escaped}\.?\b'
        
        result = re.sub(pattern, expansion, result, flags=re.IGNORECASE)
    
    # Clean up any double spaces created by replacements
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def correct_spelling(text: str, use_fuzzy: bool = True, threshold: int = 80) -> str:
    """
    Perform lightweight spell correction on address text.
    
    Uses two strategies:
    1. Direct lookup in misspelling map (fast, high precision)
    2. Fuzzy matching against dictionary (slower, catches novel errors)
    
    Args:
        text: Address text to correct
        use_fuzzy: Whether to use fuzzy matching (requires rapidfuzz)
        threshold: Minimum similarity score for fuzzy matches (0-100)
        
    Returns:
        Text with spelling corrections applied
        
    ML Note: We use a conservative threshold (80%) to avoid false corrections.
    Address text often contains proper nouns and transliterations that
    shouldn't be "corrected" to dictionary words.
    """
    if not text:
        return ""
    
    words = text.split()
    corrected_words = []
    
    # Try importing rapidfuzz for fuzzy matching
    fuzzy_available = False
    if use_fuzzy:
        try:
            from rapidfuzz import fuzz, process
            fuzzy_available = True
        except ImportError:
            pass
    
    for word in words:
        # Skip very short words, numbers, or words with digits
        if len(word) <= 2 or any(c.isdigit() for c in word):
            corrected_words.append(word)
            continue
        
        # Strategy 1: Direct misspelling lookup
        if word in MISSPELLING_MAP:
            corrected_words.append(MISSPELLING_MAP[word])
            continue
        
        # Strategy 2: Check if already correct
        if word in SPELLING_DICTIONARY:
            corrected_words.append(word)
            continue
        
        # Strategy 3: Fuzzy matching (if enabled and available)
        if fuzzy_available:
            result = process.extractOne(
                word,
                SPELLING_DICTIONARY,
                scorer=fuzz.ratio,
                score_cutoff=threshold
            )
            if result:
                corrected_words.append(result[0])
                continue
        
        # No correction found, keep original
        corrected_words.append(word)
    
    return ' '.join(corrected_words)


def extract_address_components(text: str) -> Dict[str, Any]:
    """
    Extract structured components from address text using rule-based patterns.
    
    Extracts:
    - Landmark phrases: "near temple", "behind station"
    - Direction words: "near", "behind", "opposite"
    - Street info: Lane numbers, building numbers
    
    Args:
        text: Address text (should be cleaned and expanded first)
        
    Returns:
        Dict with keys: landmarks, directions, street_info
        
    ML Note: Rule-based extraction is preferred here because:
    1. Pattern structure is well-defined (direction + noun phrase)
    2. No training data required
    3. Easy to debug and extend
    4. High precision for known patterns
    """
    if not text:
        return {"landmarks": [], "directions": [], "street_info": {}}
    
    landmarks = []
    directions = []
    street_info = {}
    
    # Extract landmark phrases (e.g., "near temple", "behind station")
    for match in LANDMARK_PHRASE_PATTERN.finditer(text):
        direction_word = match.group(1).lower()
        landmark_text = match.group(2).strip()
        
        # Skip very short or numeric-only landmarks
        if len(landmark_text) < 3 or landmark_text.replace(' ', '').isdigit():
            continue
        
        landmarks.append({
            "phrase": f"{direction_word} {landmark_text}",
            "direction": direction_word,
            "landmark": landmark_text,
            "position": match.span(),
        })
        
        # Track unique directions
        if direction_word not in directions:
            directions.append(direction_word)
    
    # Add any standalone direction words not captured in landmark phrases
    for direction in DIRECTION_WORDS:
        if direction in text.lower() and direction not in directions:
            directions.append(direction)
    
    # Extract street/lane numbers
    street_numbers = []
    for match in STREET_NUMBER_PATTERN.finditer(text):
        groups = match.groups()
        # Pattern matches either "1st lane" or "lane no 5" formats
        if groups[0]:  # "1st lane" format
            number = groups[0]
            street_type = groups[1].lower()
        else:  # "lane no 5" format
            street_type = groups[2].lower()
            number = groups[3]
        
        street_numbers.append({
            "number": number,
            "type": street_type,
            "text": match.group(0),
        })
    
    if street_numbers:
        street_info["street_numbers"] = street_numbers
    
    # Extract building/flat numbers
    building_numbers = []
    for match in BUILDING_NUMBER_PATTERN.finditer(text):
        building_numbers.append({
            "number": match.group(1),
            "text": match.group(0),
        })
    
    if building_numbers:
        street_info["building_numbers"] = building_numbers
    
    return {
        "landmarks": landmarks,
        "directions": directions,
        "street_info": street_info,
    }


# =============================================================================
# MAIN NORMALIZER FUNCTION
# =============================================================================

def normalize_address(
    raw_address: str,
    expand_abbrevs: bool = True,
    spell_correct: bool = True,
    extract_components: bool = True,
    custom_abbreviations: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    Full address normalization pipeline.
    
    Applies all normalization steps in sequence:
    1. Clean text (lowercase, whitespace, punctuation)
    2. Expand abbreviations (rd → road, etc.)
    3. Correct spelling (optional fuzzy correction)
    4. Extract structured components (landmarks, directions, street info)
    
    Args:
        raw_address: Original messy address text
        expand_abbrevs: Whether to expand abbreviations
        spell_correct: Whether to apply spell correction
        extract_components: Whether to extract structured components
        custom_abbreviations: Additional abbreviation mappings
        
    Returns:
        Dict with: clean_text, landmarks, directions, street_info, original
        
    Example:
        >>> result = normalize_address("nr shiv temple, 2nd gali, opp rly stn")
        >>> result['clean_text']
        'near shiv temple, 2nd lane, opposite railway station'
        >>> result['landmarks']
        [{'phrase': 'near shiv temple', ...}, {'phrase': 'opposite railway station', ...}]
    """
    if not raw_address:
        return {
            "clean_text": "",
            "landmarks": [],
            "directions": [],
            "street_info": {},
            "original": raw_address,
        }
    
    # Store original
    original = raw_address
    
    # Step 1: Basic cleaning
    text = clean_text(raw_address)
    
    # Step 2: Expand abbreviations
    if expand_abbrevs:
        text = expand_abbreviations(text, custom_abbreviations)
    
    # Step 3: Spell correction
    if spell_correct:
        text = correct_spelling(text)
    
    # Step 4: Extract components
    components = {"landmarks": [], "directions": [], "street_info": {}}
    if extract_components:
        components = extract_address_components(text)
    
    return {
        "clean_text": text,
        "landmarks": components["landmarks"],
        "directions": components["directions"],
        "street_info": components["street_info"],
        "original": original,
    }


# =============================================================================
# CONVENIENCE ALIASES
# =============================================================================

# Alias for backward compatibility with module naming
process = normalize_address


if __name__ == "__main__":
    # Quick demo
    test_addresses = [
        "nr shiv temple, 2nd gali, opp rly stn, mumbai",
        "H.No. 42, behind big markt, 1st lane, nagr colony",
        "flat 203, opp hosptal, nxt to scool, main rd",
    ]
    
    print("Address Normalizer Demo")
    print("=" * 50)
    
    for addr in test_addresses:
        print(f"\nInput: {addr}")
        result = normalize_address(addr)
        print(f"Clean: {result['clean_text']}")
        print(f"Landmarks: {[lm['phrase'] for lm in result['landmarks']]}")
        print(f"Directions: {result['directions']}")
        print(f"Street Info: {result['street_info']}")
