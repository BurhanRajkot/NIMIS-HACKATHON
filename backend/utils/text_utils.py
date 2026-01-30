"""
Text utility functions for address processing.
"""

import re
import unicodedata


def normalize_text(text):
    """
    Normalize text by converting to lowercase and removing extra whitespace.
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def remove_punctuation(text, keep_chars=None):
    """
    Remove punctuation from text while optionally keeping specific characters.
    
    Args:
        text: Input text string
        keep_chars: String of characters to keep (e.g., "'-")
        
    Returns:
        Text with punctuation removed
    """
    if not text:
        return ""
    
    if keep_chars is None:
        keep_chars = ""
    
    # Build pattern to match punctuation except kept characters
    pattern = r'[^\w\s' + re.escape(keep_chars) + ']'
    text = re.sub(pattern, ' ', text)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_numbers(text):
    """
    Extract all numbers from text.
    
    Args:
        text: Input text string
        
    Returns:
        List of numbers found in text
    """
    if not text:
        return []
    
    # Find all numbers (including decimals)
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    return [float(n) if '.' in n else int(n) for n in numbers]


def replace_abbreviations(text):
    """
    Replace common Indian address abbreviations with full forms.
    
    Args:
        text: Input text string
        
    Returns:
        Text with abbreviations expanded
    """
    if not text:
        return ""
    
    abbreviations = {
        r'\brd\b': 'road',
        r'\bst\b': 'street',
        r'\bln\b': 'lane',
        r'\bmg\b': 'mahatma gandhi',
        r'\bab\b': 'agra bombay',
        r'\brnt\b': 'rani sati',
        r'\bnr\b': 'near',
        r'\bopp\b': 'opposite',
        r'\bbhd\b': 'behind',
        r'\bbld\b': 'building',
        r'\bblg\b': 'building',
        r'\bapt\b': 'apartment',
        r'\bflr\b': 'floor',
        r'\bgf\b': 'ground floor',
        r'\bff\b': 'first floor',
        r'\bsf\b': 'second floor',
        r'\bhno\b': 'house number',
        r'\bh\.no\b': 'house number',
        r'\bh no\b': 'house number',
        r'\bplz\b': 'plaza',
        r'\bmkt\b': 'market',
        r'\bext\b': 'extension',
        r'\bextn\b': 'extension',
        r'\bsec\b': 'sector',
        r'\bph\b': 'phase',
        r'\bsqr\b': 'square',
        r'\bsq\b': 'square',
        r'\bchk\b': 'chowk',
        r'\bngr\b': 'nagar',
        r'\bcolny\b': 'colony',
        r'\bcol\b': 'colony',
    }
    
    result = text.lower()
    for pattern, replacement in abbreviations.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


def extract_lane_number(text):
    """
    Extract lane/gali number from address text.
    
    Args:
        text: Input text string
        
    Returns:
        Lane number as string or None
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Patterns for lane numbers
    patterns = [
        r'(\d+)(?:st|nd|rd|th)?\s*(?:lane|gali|galli)',
        r'(?:lane|gali|galli)\s*(?:no\.?\s*)?(\d+)',
        r'(?:lane|gali|galli)\s*#?\s*(\d+)',
        r'gali\s*(?:number|no\.?)?\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)
    
    return None


def extract_house_number(text):
    """
    Extract house/plot number from address text.
    
    Args:
        text: Input text string
        
    Returns:
        House number as string or None
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Patterns for house numbers
    patterns = [
        r'(?:house|h\.?\s*no?\.?|plot|flat)\s*[:#]?\s*(\d+[a-z]?)',
        r'(?:no\.?|#)\s*(\d+[a-z]?)\s*(?:,|$)',
        r'^(\d+[a-z]?)\s*(?:,|/)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1).upper()
    
    return None


def fuzzy_match_score(text1, text2):
    """
    Calculate a simple fuzzy match score between two texts.
    Uses character-level matching without external ML libraries.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize both texts
    t1 = normalize_text(text1)
    t2 = normalize_text(text2)
    
    if t1 == t2:
        return 1.0
    
    # Check for substring match
    if t1 in t2 or t2 in t1:
        shorter = min(len(t1), len(t2))
        longer = max(len(t1), len(t2))
        return shorter / longer
    
    # Character-level similarity (Jaccard-like)
    words1 = set(t1.split())
    words2 = set(t2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def contains_any(text, keywords):
    """
    Check if text contains any of the given keywords.
    
    Args:
        text: Input text string
        keywords: List of keywords to search for
        
    Returns:
        True if any keyword is found, False otherwise
    """
    if not text or not keywords:
        return False
    
    text_lower = normalize_text(text)
    
    for keyword in keywords:
        if normalize_text(keyword) in text_lower:
            return True
    
    return False


def split_address_components(text):
    """
    Split address into components based on common delimiters.
    
    Args:
        text: Input address string
        
    Returns:
        List of address components
    """
    if not text:
        return []
    
    # Split by common delimiters
    components = re.split(r'[,;/|]', text)
    
    # Clean up each component
    components = [c.strip() for c in components if c.strip()]
    
    return components
