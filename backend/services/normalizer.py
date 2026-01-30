"""
Address normalizer service - standardizes address text.
"""

import re
from utils.text_utils import replace_abbreviations, normalize_text


class AddressNormalizer:
    """
    Normalizes and standardizes address text.
    """
    
    def __init__(self, db_session=None):
        """
        Initialize the normalizer.
        
        Args:
            db_session: Database session for locality alias lookups
        """
        self.db_session = db_session
    
    def normalize(self, parsed_address, city=None):
        """
        Normalize a parsed address.
        
        Args:
            parsed_address: Dictionary from AddressParser
            city: City name for locality alias lookups
            
        Returns:
            Dictionary with normalized address components
        """
        if not parsed_address:
            return self._empty_result()
        
        raw = parsed_address.get('raw_address', '')
        
        # Step 1: Fix abbreviations
        expanded = replace_abbreviations(raw)
        
        # Step 2: Normalize casing
        normalized = self._normalize_casing(expanded)
        
        # Step 3: Apply locality aliases
        if city and self.db_session:
            normalized = self._apply_locality_aliases(normalized, city)
        
        # Step 4: Standardize punctuation
        standardized = self._standardize_punctuation(normalized)
        
        # Step 5: Build standardized address
        standardized_address = self._build_standardized_address(
            parsed_address, standardized, city
        )
        
        return {
            'original': raw,
            'expanded': expanded,
            'normalized': normalized,
            'standardized_address': standardized_address
        }
    
    def _normalize_casing(self, text):
        """
        Apply proper casing to address text.
        
        Args:
            text: Input text
            
        Returns:
            Text with proper casing
        """
        if not text:
            return ""
        
        # Title case, but keep some words lowercase
        words = text.split()
        lowercase_words = {'of', 'the', 'and', 'in', 'at', 'to', 'for', 'on', 'by'}
        
        result = []
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in lowercase_words:
                result.append(word.capitalize())
            else:
                result.append(word.lower())
        
        return ' '.join(result)
    
    def _apply_locality_aliases(self, text, city):
        """
        Replace locality aliases with canonical names.
        
        Args:
            text: Input text
            city: City for scoped lookup
            
        Returns:
            Text with aliases replaced
        """
        from database.models import LocalityAlias
        
        try:
            aliases = self.db_session.query(LocalityAlias).filter(
                LocalityAlias.city.ilike(city)
            ).all()
            
            for alias_record in aliases:
                pattern = rf'\b{re.escape(alias_record.alias)}\b'
                text = re.sub(
                    pattern, 
                    alias_record.canonical_name, 
                    text, 
                    flags=re.IGNORECASE
                )
            
        except Exception:
            # If DB lookup fails, return text as-is
            pass
        
        return text
    
    def _standardize_punctuation(self, text):
        """
        Standardize punctuation in address.
        
        Args:
            text: Input text
            
        Returns:
            Text with standardized punctuation
        """
        if not text:
            return ""
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Standardize comma spacing
        text = re.sub(r'\s*,\s*', ', ', text)
        
        # Remove trailing punctuation
        text = text.strip(' ,;/')
        
        return text
    
    def _build_standardized_address(self, parsed_address, normalized_text, city):
        """
        Build a standardized address string from components.
        
        Args:
            parsed_address: Original parsed address
            normalized_text: Normalized text
            city: City name
            
        Returns:
            Standardized address string
        """
        components = []
        
        # Add lane number if present
        lane = parsed_address.get('lane_number')
        if lane:
            components.append(f"Lane {lane}")
        
        # Add house number if present
        house = parsed_address.get('house_number')
        if house:
            components.append(f"#{house}")
        
        # Add direction + landmark combinations
        directions = parsed_address.get('directions', [])
        landmarks = parsed_address.get('landmarks', [])
        
        for i, landmark in enumerate(landmarks):
            direction = directions[i] if i < len(directions) else ""
            if direction:
                components.append(f"{direction.capitalize()} {self._normalize_casing(landmark)}")
            else:
                components.append(self._normalize_casing(landmark))
        
        # Add locality if present
        locality = parsed_address.get('locality')
        if locality:
            components.append(self._normalize_casing(locality))
        
        # Add city
        if city:
            components.append(city.title())
        
        # If no components extracted, use normalized text
        if not components:
            return normalized_text + (f", {city.title()}" if city else "")
        
        return ', '.join(components)
    
    def _empty_result(self):
        """Return an empty normalization result."""
        return {
            'original': '',
            'expanded': '',
            'normalized': '',
            'standardized_address': ''
        }
