"""
Shared utilities for geospatial NLP processing.

Contains helper functions used across all modules:
- Text cleaning and preprocessing
- Geographic calculations
- Pincode validation
- State/district lookups
"""

import re
import math
import json
import unicodedata
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from functools import lru_cache

# Get the data directory path relative to this file
DATA_DIR = Path(__file__).parent / "data"


# =============================================================================
# TEXT UTILITIES
# =============================================================================

def clean_text(text: str) -> str:
    """
    Basic text cleaning: lowercase, normalize whitespace, strip edges.
    
    We preserve most punctuation as it can be meaningful in addresses
    (e.g., hyphens in pincodes, slashes in building numbers).
    """
    if not text:
        return ""
    
    # Normalize unicode (important for Devanagari and other Indian scripts)
    text = unicodedata.normalize("NFKC", text)
    
    # Lowercase for consistent matching
    text = text.lower()
    
    # Normalize whitespace (multiple spaces, tabs, newlines -> single space)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def remove_special_chars(text: str, keep_chars: str = ".,/-#") -> str:
    """
    Remove special characters while keeping address-relevant punctuation.
    
    Args:
        text: Input text
        keep_chars: Characters to preserve (default includes common address punctuation)
    """
    # Build pattern to remove chars not in: alphanumeric, space, or keep_chars
    escaped_keep = re.escape(keep_chars)
    pattern = rf'[^\w\s{escaped_keep}]'
    
    return re.sub(pattern, '', text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces and trim."""
    return re.sub(r'\s+', ' ', text).strip()


# =============================================================================
# GEOGRAPHIC UTILITIES  
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Uses the Haversine formula which is accurate for small distances
    (unlike flat-earth approximations).
    
    Args:
        lat1, lon1: First point coordinates in degrees
        lat2, lon2: Second point coordinates in degrees
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def is_within_india(lat: float, lon: float) -> bool:
    """
    Quick bounds check if coordinates are roughly within India.
    
    India's approximate bounding box:
    - Latitude: 6°N to 36°N
    - Longitude: 68°E to 98°E
    
    This is a coarse filter to catch obviously wrong geocoding results.
    """
    return 6.0 <= lat <= 36.0 and 68.0 <= lon <= 98.0


# =============================================================================
# PINCODE UTILITIES
# =============================================================================

def validate_pincode(pincode: str) -> bool:
    """
    Validate Indian pincode format.
    
    Indian pincodes are 6 digits where:
    - First digit: 1-9 (region code, 0 is not used)
    - Remaining 5 digits: 0-9
    
    This doesn't check if the pincode actually exists, just format validity.
    """
    if not pincode:
        return False
    
    # Remove any spaces or hyphens that might be present
    pincode = re.sub(r'[\s\-]', '', str(pincode))
    
    # Must be exactly 6 digits, first digit 1-9
    return bool(re.match(r'^[1-9]\d{5}$', pincode))


def extract_pincode(text: str) -> Optional[str]:
    """
    Extract the first valid pincode from text.
    
    Handles common formats:
    - "400001" (plain)
    - "400-001" (hyphenated)
    - "mumbai - 400001" (city prefix)
    - "pin: 400001" (with label)
    """
    # Pattern matches 6-digit sequences that look like pincodes
    # Negative lookbehind/ahead to avoid matching phone numbers
    patterns = [
        r'\b([1-9]\d{5})\b',  # Plain 6 digits
        r'\b([1-9]\d{2})[\s\-]?(\d{3})\b',  # With separator
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            # Join groups if split by separator
            pincode = ''.join(match.groups())
            if validate_pincode(pincode):
                return pincode
    
    return None


def get_pincode_region(pincode: str) -> Optional[str]:
    """
    Get the postal region from a pincode's first digit.
    
    Indian pincode regions:
    1 - Delhi, Haryana, Punjab, HP, J&K, Chandigarh
    2 - UP, Uttarakhand
    3 - Rajasthan, Gujarat, Daman & Diu
    4 - Maharashtra, MP, Chhattisgarh, Goa
    5 - Andhra, Karnataka, Telangana
    6 - Kerala, Tamil Nadu, Pondicherry, Lakshadweep
    7 - West Bengal, Odisha, NE States, A&N Islands
    8 - Bihar, Jharkhand
    9 - Army Post Offices (APO/FPO)
    """
    if not validate_pincode(pincode):
        return None
    
    regions = {
        '1': 'Northern',
        '2': 'Uttar Pradesh',
        '3': 'Western',
        '4': 'Western-Central',
        '5': 'Southern',
        '6': 'Southern',
        '7': 'Eastern',
        '8': 'Eastern',
        '9': 'APO/FPO',
    }
    
    return regions.get(pincode[0])


# =============================================================================
# DATA LOADING UTILITIES
# =============================================================================

@lru_cache(maxsize=1)
def load_indian_states() -> Dict[str, dict]:
    """
    Load state data from JSON file.
    
    Returns dict mapping state codes to state info including:
    - name: Full state name
    - aliases: Common abbreviations and alternate names
    - capital: State capital
    """
    try:
        with open(DATA_DIR / "indian_states.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return minimal fallback data if file not found
        return _get_fallback_states()


def _get_fallback_states() -> Dict[str, dict]:
    """Fallback state data if JSON file is missing."""
    return {
        "MH": {"name": "Maharashtra", "aliases": ["mh", "maha", "maharashtra"], "capital": "Mumbai"},
        "DL": {"name": "Delhi", "aliases": ["dl", "delhi", "new delhi", "ncr"], "capital": "New Delhi"},
        "KA": {"name": "Karnataka", "aliases": ["ka", "karnataka", "ktk"], "capital": "Bengaluru"},
        "TN": {"name": "Tamil Nadu", "aliases": ["tn", "tamilnadu", "tamil nadu"], "capital": "Chennai"},
        "UP": {"name": "Uttar Pradesh", "aliases": ["up", "uttar pradesh"], "capital": "Lucknow"},
        "GJ": {"name": "Gujarat", "aliases": ["gj", "gujarat", "guj"], "capital": "Gandhinagar"},
        "RJ": {"name": "Rajasthan", "aliases": ["rj", "rajasthan", "raj"], "capital": "Jaipur"},
        "WB": {"name": "West Bengal", "aliases": ["wb", "west bengal", "bengal"], "capital": "Kolkata"},
        "AP": {"name": "Andhra Pradesh", "aliases": ["ap", "andhra", "andhra pradesh"], "capital": "Amaravati"},
        "TS": {"name": "Telangana", "aliases": ["ts", "telangana", "tg"], "capital": "Hyderabad"},
        "KL": {"name": "Kerala", "aliases": ["kl", "kerala"], "capital": "Thiruvananthapuram"},
        "MP": {"name": "Madhya Pradesh", "aliases": ["mp", "madhya pradesh"], "capital": "Bhopal"},
        "BR": {"name": "Bihar", "aliases": ["br", "bihar"], "capital": "Patna"},
        "PB": {"name": "Punjab", "aliases": ["pb", "punjab"], "capital": "Chandigarh"},
        "HR": {"name": "Haryana", "aliases": ["hr", "haryana"], "capital": "Chandigarh"},
    }


@lru_cache(maxsize=1)
def load_landmark_patterns() -> Dict[str, List[str]]:
    """
    Load landmark patterns from JSON file.
    
    Returns dict mapping landmark categories to pattern lists.
    """
    try:
        with open(DATA_DIR / "landmarks.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return _get_fallback_landmarks()


def _get_fallback_landmarks() -> Dict[str, List[str]]:
    """Fallback landmark patterns if JSON file is missing."""
    return {
        "religious": ["temple", "mandir", "masjid", "mosque", "church", "gurudwara", "dargah"],
        "transport": ["railway station", "bus stand", "bus stop", "metro station", "airport"],
        "commercial": ["market", "mall", "shop", "bazaar", "mandi"],
        "education": ["school", "college", "university", "vidyalaya", "institute"],
        "health": ["hospital", "clinic", "dispensary", "medical"],
        "government": ["police station", "post office", "court", "collector office"],
        "infrastructure": ["bridge", "flyover", "signal", "chowk", "circle", "square"],
    }


@lru_cache(maxsize=1)
def load_pincode_centroids() -> Dict[str, Tuple[float, float]]:
    """
    Load pincode to centroid coordinate mappings.
    
    Returns dict mapping pincode strings to (lat, lon) tuples.
    """
    try:
        with open(DATA_DIR / "pincode_centroids.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {k: tuple(v) for k, v in data.items()}
    except FileNotFoundError:
        return _get_fallback_pincodes()


def _get_fallback_pincodes() -> Dict[str, Tuple[float, float]]:
    """Fallback pincode data - major city pincodes."""
    return {
        # Mumbai
        "400001": (18.9398, 72.8354),  # Fort
        "400069": (19.1136, 72.8697),  # Andheri East
        "400028": (19.0178, 72.8478),  # Dadar
        # Delhi
        "110001": (28.6358, 77.2245),  # Connaught Place
        "110020": (28.5672, 77.2100),  # Hauz Khas
        # Bengaluru
        "560001": (12.9767, 77.5713),  # MG Road
        "560034": (12.9352, 77.6245),  # Koramangala
        # Chennai
        "600001": (13.0878, 80.2785),  # Parrys
        # Hyderabad
        "500001": (17.3850, 78.4867),  # Abids
        # Kolkata
        "700001": (22.5726, 88.3639),  # BBD Bagh
        # Pune
        "411001": (18.5204, 73.8567),  # Camp
    }


def resolve_state_name(text: str) -> Optional[str]:
    """
    Try to identify a state from text using aliases.
    
    Returns the canonical state code (e.g., "MH" for Maharashtra).
    """
    text_lower = text.lower().strip()
    states = load_indian_states()
    
    for code, info in states.items():
        # Check against full name and all aliases
        if text_lower == info["name"].lower():
            return code
        if text_lower in [a.lower() for a in info.get("aliases", [])]:
            return code
    
    return None
