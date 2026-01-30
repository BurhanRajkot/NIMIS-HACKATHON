"""
Address parser service - extracts structured components from raw addresses.
"""

import re
from utils.text_utils import normalize_text, extract_lane_number, extract_house_number


class AddressParser:
    """
    Parses raw address text to extract landmarks, directions, and other components.
    """
    
    # Direction keywords used in Indian addresses
    DIRECTION_KEYWORDS = [
        'near', 'behind', 'after', 'before', 'opposite', 'opp',
        'next to', 'beside', 'in front of', 'front', 'back',
        'left', 'right', 'adjacent', 'across', 'facing'
    ]
    
    # Common landmark type indicators
    LANDMARK_INDICATORS = [
        'temple', 'mandir', 'masjid', 'mosque', 'church', 'gurudwara',
        'mall', 'market', 'bazaar', 'shop', 'store', 'stall',
        'hospital', 'clinic', 'school', 'college', 'university',
        'bank', 'atm', 'petrol pump', 'gas station',
        'park', 'garden', 'ground', 'stadium',
        'police station', 'post office', 'cinema', 'theatre',
        'hotel', 'restaurant', 'dhaba', 'cafe',
        'bus stand', 'railway station', 'metro station',
        'chowk', 'square', 'circle', 'crossing',
        'tower', 'building', 'complex', 'apartment',
        'gate', 'naka', 'bridge', 'flyover'
    ]
    
    def __init__(self):
        """Initialize the address parser."""
        pass
    
    def parse(self, raw_address):
        """
        Parse a raw address and extract structured components.
        
        Args:
            raw_address: Raw address string
            
        Returns:
            Dictionary with parsed components
        """
        if not raw_address:
            return self._empty_result()
        
        normalized = normalize_text(raw_address)
        
        result = {
            'raw_address': raw_address,
            'normalized': normalized,
            'landmarks': self._extract_landmarks(normalized),
            'directions': self._extract_directions(normalized),
            'lane_number': extract_lane_number(normalized),
            'house_number': extract_house_number(normalized),
            'locality': self._extract_locality(normalized),
            'components': self._split_into_components(normalized)
        }
        
        return result
    
    def _extract_landmarks(self, text):
        """
        Extract potential landmark references from text.
        
        Args:
            text: Normalized address text
            
        Returns:
            List of potential landmark strings
        """
        landmarks = []
        
        # Pattern: direction keyword followed by landmark
        for direction in self.DIRECTION_KEYWORDS:
            pattern = rf'{direction}\s+(.+?)(?:,|$|\s+(?:{"|".join(self.DIRECTION_KEYWORDS)}))'
            matches = re.findall(pattern, text, re.IGNORECASE)
            landmarks.extend([m.strip() for m in matches if m.strip()])
        
        # Pattern: landmark indicator words
        for indicator in self.LANDMARK_INDICATORS:
            pattern = rf'(\b\w+\s+{indicator}\b|\b{indicator}\s+\w+\b)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            landmarks.extend([m.strip() for m in matches if m.strip()])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_landmarks = []
        for lm in landmarks:
            lm_lower = lm.lower()
            if lm_lower not in seen:
                seen.add(lm_lower)
                unique_landmarks.append(lm)
        
        return unique_landmarks
    
    def _extract_directions(self, text):
        """
        Extract directional keywords from text.
        
        Args:
            text: Normalized address text
            
        Returns:
            List of direction keywords found
        """
        found_directions = []
        
        for direction in self.DIRECTION_KEYWORDS:
            if re.search(rf'\b{direction}\b', text, re.IGNORECASE):
                found_directions.append(direction)
        
        return found_directions
    
    def _extract_locality(self, text):
        """
        Try to extract locality/area name from text.
        
        Args:
            text: Normalized address text
            
        Returns:
            Extracted locality or None
        """
        # Common locality patterns
        patterns = [
            r'(\w+\s*nagar)',
            r'(\w+\s*colony)',
            r'(\w+\s*vihar)',
            r'(\w+\s*enclave)',
            r'(\w+\s*extension)',
            r'(\w+\s*sector)',
            r'scheme\s*(?:no\.?)?\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _split_into_components(self, text):
        """
        Split address into logical components.
        
        Args:
            text: Normalized address text
            
        Returns:
            List of address components
        """
        # Split by common delimiters
        components = re.split(r'[,;/]', text)
        
        # Clean up each component
        components = [c.strip() for c in components if c.strip()]
        
        return components
    
    def _empty_result(self):
        """Return an empty parse result."""
        return {
            'raw_address': '',
            'normalized': '',
            'landmarks': [],
            'directions': [],
            'lane_number': None,
            'house_number': None,
            'locality': None,
            'components': []
        }
