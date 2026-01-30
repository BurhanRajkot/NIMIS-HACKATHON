"""
Address Text Normalizer for Indian Addresses.

Handles the messy reality of Indian address text:
- Mixed languages (Hindi/English/regional)
- Inconsistent abbreviations (Rd, Opp, Nr, etc.)
- Transliterations (gali, chowk, mohalla)
- Various pincode formats
- Noisy punctuation and casing

Approach: Rule-based transformations + regex patterns
(No ML training needed, fast and interpretable)
"""

import re
from typing import Dict, Optional, List, Tuple
from .utils import (
    clean_text,
    normalize_whitespace,
    extract_pincode,
    resolve_state_name,
    load_indian_states,
)


# =============================================================================
# ABBREVIATION MAPPINGS
# =============================================================================

# Common English abbreviations found in Indian addresses
ENGLISH_ABBREVIATIONS = {
    # Directional
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "ne": "northeast",
    "nw": "northwest",
    "se": "southeast",
    "sw": "southwest",
    
    # Road types
    "rd": "road",
    "st": "street",
    "ln": "lane",
    "ave": "avenue",
    "blvd": "boulevard",
    "hwy": "highway",
    "nh": "national highway",
    "sh": "state highway",
    
    # Building types
    "bldg": "building",
    "blk": "block",
    "flr": "floor",
    "fl": "floor",
    "apt": "apartment",
    "appt": "apartment",
    "flat": "flat",
    "flt": "flat",
    "hse": "house",
    "hno": "house number",
    "h.no": "house number",
    
    # Positional
    "nr": "near",
    "opp": "opposite",
    "adj": "adjacent",
    "bhnd": "behind",
    "b/h": "behind",
    "bh": "behind",
    "nxt": "next to",
    "beside": "beside",
    
    # Areas
    "sec": "sector",
    "ph": "phase",
    "extn": "extension",
    "ext": "extension",
    "plt": "plot",
    "dist": "district",
    "div": "division",
    "taluk": "taluk",
    "tq": "taluk",
    "mandal": "mandal",
    
    # Post-related
    "po": "post office",
    "p.o": "post office",
    "ps": "police station",
    "p.s": "police station",
    "pin": "pincode",
    
    # Common shortcuts
    "mkt": "market",
    "stn": "station",
    "rly": "railway",
    "hosp": "hospital",
    "govt": "government",
    "pvt": "private",
    "ltd": "limited",
    "co": "company",
    "ind": "industrial",
    "indl": "industrial",
    "comm": "commercial",
    "res": "residential",
    "soc": "society",
    "chs": "cooperative housing society",
    "chsl": "cooperative housing society limited",
}

# Hindi/Indian language transliterations commonly found in addresses
TRANSLITERATIONS = {
    # Street/Lane types
    "gali": "lane",
    "gully": "lane",
    "marg": "road",
    "path": "road",
    "sadak": "road",
    "rasta": "road",
    
    # Area types
    "mohalla": "locality",
    "mohala": "locality",
    "para": "locality",
    "nagar": "colony",
    "puram": "colony",
    "puri": "colony",
    "wadi": "colony",
    "wada": "colony",
    "peth": "area",
    "pet": "area",
    "bagh": "garden area",
    "vihar": "residential area",
    "kunj": "residential area",
    "enclave": "enclave",
    
    # Landmarks
    "chowk": "square",
    "chawk": "square",
    "chauk": "square",
    "tiraha": "three-way junction",
    "morh": "turn",
    "mod": "turn",
    "pul": "bridge",
    "pull": "bridge",
    "maidan": "ground",
    "kund": "pond area",
    "talaab": "lake area",
    "talab": "lake area",
    
    # Building types
    "bhavan": "building",
    "bhawan": "building",
    "sadan": "building",
    "ghar": "house",
    "kothi": "bungalow",
    "haveli": "mansion",
    "dukan": "shop",
    
    # Religious
    "mandir": "temple",
    "masjid": "mosque",
    "gurudwara": "gurudwara",
    "dargah": "dargah",
    
    # Commercial
    "bazaar": "market",
    "bazar": "market",
    "mandi": "market",
    "haat": "market",
    
    # Directions (Hindi)
    "uttar": "north",
    "dakshin": "south",
    "purv": "east",
    "paschim": "west",
}

# Common city name variations and their canonical forms
CITY_ALIASES = {
    "bombay": "mumbai",
    "madras": "chennai",
    "calcutta": "kolkata",
    "bangalore": "bengaluru",
    "trivandrum": "thiruvananthapuram",
    "baroda": "vadodara",
    "cochin": "kochi",
    "poona": "pune",
    "shimoga": "shivamogga",
    "belgaum": "belagavi",
    "mysore": "mysuru",
    "mangalore": "mangaluru",
    "vizag": "visakhapatnam",
    "pondicherry": "puducherry",
    "banaras": "varanasi",
    "benares": "varanasi",
    "allahabad": "prayagraj",
    "gurgaon": "gurugram",
}


# =============================================================================
# NORMALIZER CLASS
# =============================================================================

class AddressNormalizer:
    """
    Normalizes messy Indian address text into a cleaner, standardized form.
    
    This is a rule-based normalizer that applies a series of transformations:
    1. Unicode normalization
    2. Case normalization  
    3. Abbreviation expansion
    4. Transliteration handling
    5. Pincode extraction
    6. State/city identification
    7. Noise removal
    
    No ML model needed - fast, interpretable, and handles common patterns well.
    """
    
    def __init__(
        self,
        expand_abbreviations: bool = True,
        translate_hindi: bool = True,
        normalize_cities: bool = True,
        extract_components: bool = True,
    ):
        """
        Initialize normalizer with configurable options.
        
        Args:
            expand_abbreviations: Expand common abbreviations (Rd -> Road)
            translate_hindi: Convert Hindi transliterations to English
            normalize_cities: Map old city names to new (Bombay -> Mumbai)
            extract_components: Extract pincode, state, city as separate fields
        """
        self.expand_abbreviations = expand_abbreviations
        self.translate_hindi = translate_hindi
        self.normalize_cities = normalize_cities
        self.extract_components = extract_components
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance."""
        # Pattern to match abbreviations as whole words
        # Uses word boundaries to avoid partial matches
        abbrev_pattern = r'\b(' + '|'.join(
            re.escape(k) for k in sorted(ENGLISH_ABBREVIATIONS.keys(), key=len, reverse=True)
        ) + r')\.?\b'
        self._abbrev_re = re.compile(abbrev_pattern, re.IGNORECASE)
        
        # Pattern for transliterations
        trans_pattern = r'\b(' + '|'.join(
            re.escape(k) for k in sorted(TRANSLITERATIONS.keys(), key=len, reverse=True)
        ) + r')\b'
        self._trans_re = re.compile(trans_pattern, re.IGNORECASE)
        
        # Pattern for city aliases
        city_pattern = r'\b(' + '|'.join(
            re.escape(k) for k in sorted(CITY_ALIASES.keys(), key=len, reverse=True)
        ) + r')\b'
        self._city_re = re.compile(city_pattern, re.IGNORECASE)
        
        # Pattern for directional suffixes like (E), (W), (N), (S)
        self._direction_suffix_re = re.compile(r'\(([ewns])\)', re.IGNORECASE)
        
        # Pattern for duplicate/noisy punctuation
        self._noise_re = re.compile(r'[,\.\-]{2,}')
        
        # Pattern for state extraction at end of address
        # Common patterns: "Maharashtra", "MH", "State: Maharashtra"
        self._state_suffix_re = re.compile(
            r'(?:state\s*:\s*)?([a-z\s]+)$',
            re.IGNORECASE
        )
    
    def normalize(self, address: str) -> Dict[str, Optional[str]]:
        """
        Normalize an address and extract components.
        
        Args:
            address: Raw address text
            
        Returns:
            Dict with keys:
            - text: Normalized address text
            - pincode: Extracted pincode (if found)
            - state: Identified state code (if found)
            - city: Identified city (if found)
            - original: Original input text
        """
        if not address:
            return {
                "text": "",
                "pincode": None,
                "state": None,
                "city": None,
                "original": address,
            }
        
        # Store original
        original = address
        
        # Step 1: Basic cleaning (unicode, lowercase, whitespace)
        text = clean_text(address)
        
        # Step 2: Extract pincode before other transformations
        # (We want to capture it before any text modifications)
        pincode = extract_pincode(text) if self.extract_components else None
        
        # Step 3: Expand directional suffixes like (E) -> East
        text = self._expand_direction_suffixes(text)
        
        # Step 4: Expand English abbreviations
        if self.expand_abbreviations:
            text = self._expand_abbreviations(text)
        
        # Step 5: Handle Hindi transliterations
        if self.translate_hindi:
            text = self._handle_transliterations(text)
        
        # Step 6: Normalize city names
        if self.normalize_cities:
            text = self._normalize_city_names(text)
        
        # Step 7: Clean up noise
        text = self._clean_noise(text)
        
        # Step 8: Extract state and city if requested
        state = None
        city = None
        if self.extract_components:
            state = self._extract_state(text)
            city = self._extract_city(text)
        
        # Final normalization pass
        text = normalize_whitespace(text)
        
        return {
            "text": text,
            "pincode": pincode,
            "state": state,
            "city": city,
            "original": original,
        }
    
    def _expand_direction_suffixes(self, text: str) -> str:
        """
        Expand directional suffixes like (E) to East.
        
        Common in Mumbai addresses: "Andheri (E)" means Andheri East
        """
        direction_map = {'e': 'east', 'w': 'west', 'n': 'north', 's': 'south'}
        
        def replace_direction(match):
            d = match.group(1).lower()
            return direction_map.get(d, match.group(0))
        
        return self._direction_suffix_re.sub(replace_direction, text)
    
    def _expand_abbreviations(self, text: str) -> str:
        """
        Expand common English abbreviations.
        
        Uses word boundaries to avoid partial replacements.
        Handles both with and without trailing periods.
        """
        def replace_abbrev(match):
            abbrev = match.group(1).lower()
            return ENGLISH_ABBREVIATIONS.get(abbrev, match.group(0))
        
        return self._abbrev_re.sub(replace_abbrev, text)
    
    def _handle_transliterations(self, text: str) -> str:
        """
        Optionally translate Hindi transliterations.
        
        Note: We keep the original term in parentheses for context,
        e.g., "gali" -> "lane (gali)" since the Hindi term might be
        useful for landmark matching.
        
        For MVP, we just translate directly without keeping original.
        """
        def replace_trans(match):
            term = match.group(1).lower()
            return TRANSLITERATIONS.get(term, match.group(0))
        
        return self._trans_re.sub(replace_trans, text)
    
    def _normalize_city_names(self, text: str) -> str:
        """
        Update old city names to current official names.
        
        e.g., Bombay -> Mumbai, Madras -> Chennai
        """
        def replace_city(match):
            city = match.group(1).lower()
            return CITY_ALIASES.get(city, match.group(0))
        
        return self._city_re.sub(replace_city, text)
    
    def _clean_noise(self, text: str) -> str:
        """
        Remove noisy punctuation while preserving meaningful structure.
        
        - Multiple consecutive punctuation (.., --, etc.)
        - Leading/trailing punctuation
        - Excessive commas
        """
        # Replace multiple punctuation with single
        text = self._noise_re.sub(lambda m: m.group(0)[0], text)
        
        # Remove leading/trailing punctuation from segments
        segments = text.split(',')
        segments = [s.strip(' .,;:-') for s in segments if s.strip()]
        text = ', '.join(segments)
        
        return text
    
    def _extract_state(self, text: str) -> Optional[str]:
        """
        Try to identify the state from the address text.
        
        Returns state code (e.g., "MH" for Maharashtra) if found.
        """
        # Common patterns where state appears
        # 1. At the end: "..., Maharashtra"
        # 2. With pincode: "Mumbai 400001 Maharashtra"
        # 3. As code: "MH" or "maha"
        
        states = load_indian_states()
        text_lower = text.lower()
        
        # Check each state's name and aliases
        for code, info in states.items():
            # Check full name
            if info["name"].lower() in text_lower:
                return code
            # Check aliases
            for alias in info.get("aliases", []):
                if f" {alias.lower()} " in f" {text_lower} ":
                    return code
        
        return None
    
    def _extract_city(self, text: str) -> Optional[str]:
        """
        Try to identify major cities from the address.
        
        Returns the canonical city name if identified.
        """
        # First check for normalized city names (already in text after normalization)
        major_cities = [
            "mumbai", "delhi", "bengaluru", "chennai", "kolkata",
            "hyderabad", "pune", "ahmedabad", "surat", "jaipur",
            "lucknow", "kanpur", "nagpur", "indore", "thane",
            "bhopal", "visakhapatnam", "patna", "vadodara", "ghaziabad",
            "ludhiana", "agra", "nashik", "faridabad", "meerut",
            "rajkot", "varanasi", "srinagar", "aurangabad", "dhanbad",
            "amritsar", "navi mumbai", "noida", "gurugram", "guwahati",
        ]
        
        text_lower = text.lower()
        for city in major_cities:
            if city in text_lower:
                return city.title()
        
        return None


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def normalize_address(address: str, **kwargs) -> Dict[str, Optional[str]]:
    """
    Convenience function to normalize an address.
    
    Args:
        address: Raw address text
        **kwargs: Options passed to AddressNormalizer
        
    Returns:
        Normalized address dict with text and extracted components
    """
    normalizer = AddressNormalizer(**kwargs)
    return normalizer.normalize(address)
