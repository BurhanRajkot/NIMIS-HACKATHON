"""
Confidence Scoring for Geocoded Addresses.

Assigns confidence scores (0-1) to geocoding results based on:
1. Quality of input signals (pincode, state, city, landmarks)
2. Geocoding method used (pincode vs. city vs. fallback)
3. Consistency between signals (do pincode and city match?)
4. Completeness of extracted information

This is a heuristic-based scorer that provides interpretable
confidence estimates without requiring ML training.

Scoring philosophy:
- Pincode-based results get highest base score
- Multiple consistent signals increase confidence
- Conflicting signals decrease confidence
- Fallback methods get low scores
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# =============================================================================
# SCORING WEIGHTS
# =============================================================================

# Base scores for different geocoding sources
# These represent confidence before considering other factors
SOURCE_BASE_SCORES = {
    "pincode": 0.85,         # Pincode is very reliable in India
    "pincode_prefix": 0.65,  # Less precise but still useful
    "city": 0.55,            # City centroid, moderate precision
    "state": 0.30,           # State centroid, low precision
    "nominatim": 0.70,       # External API, usually reliable
    "country_fallback": 0.10,  # Last resort, very low confidence
}

# Weights for different components when calculating final score
COMPONENT_WEIGHTS = {
    "pincode": 0.35,    # Pincode is most important signal
    "city": 0.20,       # City adds good context
    "state": 0.15,      # State helps validate
    "landmarks": 0.15,  # Landmarks add local context
    "consistency": 0.15,  # Agreement between signals
}

# Bonus/penalty adjustments
ADJUSTMENTS = {
    "multiple_landmarks": 0.05,      # Having 2+ landmarks increases confidence
    "pincode_city_match": 0.08,      # Pincode's city matches extracted city
    "pincode_state_match": 0.05,     # Pincode's state matches extracted state
    "conflicting_signals": -0.15,    # City and pincode region don't match
    "normalized_clean": 0.03,        # Address normalized without issues
    "has_building_number": 0.05,     # Contains specific building/house number
}


# =============================================================================
# CONFIDENCE SCORER CLASS
# =============================================================================

class ConfidenceScorer:
    """
    Calculates confidence scores for geocoding results.
    
    The scorer evaluates multiple dimensions:
    1. Source quality - How was the location determined?
    2. Signal completeness - How many address components were extracted?
    3. Signal consistency - Do the components agree with each other?
    4. Precision indicators - Are there specific details like landmarks?
    
    Final score is a weighted combination of these factors,
    bounded to [0, 1] range.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize scorer with optional custom weights.
        
        Args:
            weights: Custom component weights (uses defaults if not provided)
        """
        self.weights = weights or COMPONENT_WEIGHTS.copy()
    
    def score(
        self,
        normalized: Dict,
        landmarks: List[Dict],
        geo_result: Dict,
    ) -> Dict:
        """
        Calculate confidence score for a geocoding result.
        
        Args:
            normalized: Output from AddressNormalizer
            landmarks: Output from LandmarkExtractor
            geo_result: Output from ContextualGeocoder
            
        Returns:
            Dict with overall score and component breakdown
        """
        # Get base score from geocoding source
        source = geo_result.get("source", "country_fallback")
        base_score = SOURCE_BASE_SCORES.get(source, 0.1)
        
        # Calculate component scores
        component_scores = {
            "base": base_score,
            "pincode": self._score_pincode(normalized),
            "city": self._score_city(normalized),
            "state": self._score_state(normalized),
            "landmarks": self._score_landmarks(landmarks),
            "consistency": self._score_consistency(normalized, geo_result),
        }
        
        # Calculate adjustments
        adjustments = self._calculate_adjustments(
            normalized, landmarks, geo_result
        )
        
        # Combine scores using weights
        # Start with base score, then add weighted component contributions
        final_score = base_score
        
        for component, weight in self.weights.items():
            if component in component_scores:
                # Contribution is weight * (component_score - 0.5) * 2
                # This makes 0.5 neutral, >0.5 positive, <0.5 negative
                contribution = weight * (component_scores[component] - 0.5) * 2
                final_score += contribution
        
        # Apply adjustments
        total_adjustment = sum(adjustments.values())
        final_score += total_adjustment
        
        # Clamp to [0.05, 0.99] - never give 0% or 100% confidence
        final_score = max(0.05, min(0.99, final_score))
        
        # Determine confidence level label
        confidence_level = self._get_confidence_level(final_score)
        
        return {
            "score": round(final_score, 3),
            "level": confidence_level,
            "components": component_scores,
            "adjustments": adjustments,
            "interpretation": self._interpret_score(final_score, source),
        }
    
    def _score_pincode(self, normalized: Dict) -> float:
        """Score based on pincode extraction."""
        pincode = normalized.get("pincode")
        
        if not pincode:
            return 0.3  # No pincode is a weak signal
        
        # Valid 6-digit pincode
        if len(pincode) == 6 and pincode.isdigit():
            # First digit indicates region (1-8 valid, 9 is APO)
            if pincode[0] in "12345678":
                return 0.95
            elif pincode[0] == "9":
                return 0.80  # APO/FPO addresses
        
        return 0.4  # Invalid format
    
    def _score_city(self, normalized: Dict) -> float:
        """Score based on city extraction."""
        city = normalized.get("city")
        
        if not city:
            return 0.4  # No city extracted
        
        # Known major city
        if city.lower() in self._get_major_cities():
            return 0.9
        
        # Some city identified
        return 0.7
    
    def _score_state(self, normalized: Dict) -> float:
        """Score based on state extraction."""
        state = normalized.get("state")
        
        if not state:
            return 0.4  # No state extracted
        
        # Valid state code (2 letters)
        if len(state) == 2 and state.isalpha():
            return 0.85
        
        return 0.6
    
    def _score_landmarks(self, landmarks: List[Dict]) -> float:
        """Score based on extracted landmarks."""
        if not landmarks:
            return 0.4  # No landmarks, not necessarily bad
        
        # More landmarks = higher confidence
        # But saturates after 3-4 landmarks
        num_landmarks = len(landmarks)
        
        if num_landmarks >= 3:
            base = 0.9
        elif num_landmarks == 2:
            base = 0.8
        else:
            base = 0.7
        
        # Adjust based on landmark confidence scores
        avg_confidence = sum(
            lm.get("confidence", 0.5) for lm in landmarks
        ) / num_landmarks
        
        return base * (0.7 + 0.3 * avg_confidence)
    
    def _score_consistency(self, normalized: Dict, geo_result: Dict) -> float:
        """
        Score based on consistency between extracted components.
        
        Checks if pincode region matches city/state.
        """
        pincode = normalized.get("pincode", "")
        city = normalized.get("city", "")
        state = normalized.get("state", "")
        
        if not pincode:
            return 0.5  # Can't check consistency without pincode
        
        # Check pincode region against known data
        region_city_map = {
            "1": ["delhi", "chandigarh", "shimla", "srinagar"],  # Northern
            "2": ["lucknow", "kanpur", "agra", "noida", "ghaziabad"],  # UP
            "3": ["jaipur", "ahmedabad", "surat", "vadodara"],  # Western
            "4": ["mumbai", "pune", "nagpur", "thane", "nashik", "bhopal"],  # Western-Central
            "5": ["hyderabad", "bengaluru", "visakhapatnam"],  # Southern
            "6": ["chennai", "thiruvananthapuram", "kochi", "coimbatore"],  # Southern
            "7": ["kolkata", "bhubaneswar", "guwahati"],  # Eastern
            "8": ["patna", "ranchi"],  # Eastern
        }
        
        region = pincode[0] if pincode else ""
        expected_cities = region_city_map.get(region, [])
        
        if city.lower() in expected_cities:
            return 0.95  # City matches pincode region
        elif city and city.lower() not in [c for cities in region_city_map.values() for c in cities]:
            return 0.5  # Unknown city, neutral
        elif city:
            return 0.3  # City doesn't match region
        
        return 0.5  # No city to check
    
    def _calculate_adjustments(
        self,
        normalized: Dict,
        landmarks: List[Dict],
        geo_result: Dict,
    ) -> Dict[str, float]:
        """Calculate adjustment bonuses and penalties."""
        adjustments = {}
        
        # Multiple landmarks bonus
        if len(landmarks) >= 2:
            adjustments["multiple_landmarks"] = ADJUSTMENTS["multiple_landmarks"]
        
        # Check for building/house number in original text
        text = normalized.get("original", "")
        if self._has_building_number(text):
            adjustments["has_building_number"] = ADJUSTMENTS["has_building_number"]
        
        # Penalize if we fell back to country level
        if geo_result.get("source") == "country_fallback":
            adjustments["fallback_penalty"] = -0.2
        
        return adjustments
    
    def _has_building_number(self, text: str) -> bool:
        """Check if address contains a building/house number."""
        import re
        
        # Common patterns for building numbers in Indian addresses
        patterns = [
            r'\b\d+[/-]?\d*\s*,',  # "42, " or "42/3, "
            r'\bhno?\s*\.?\s*\d+',  # "H.No. 42" or "HNo 42"
            r'\bflat\s*(?:no\.?)?\s*\d+',  # "Flat No. 203"
            r'\bplot\s*(?:no\.?)?\s*\d+',  # "Plot No. 15"
            r'\bblock\s*[a-z]?\s*[-]?\s*\d+',  # "Block A-12"
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _get_major_cities(self) -> set:
        """Get set of major city names for validation."""
        return {
            "mumbai", "delhi", "bengaluru", "chennai", "kolkata",
            "hyderabad", "pune", "ahmedabad", "surat", "jaipur",
            "lucknow", "kanpur", "nagpur", "indore", "thane",
            "bhopal", "visakhapatnam", "patna", "vadodara", "ghaziabad",
            "noida", "gurugram", "chandigarh", "coimbatore", "kochi",
        }
    
    def _get_confidence_level(self, score: float) -> str:
        """Map numeric score to confidence level label."""
        if score >= 0.85:
            return "high"
        elif score >= 0.65:
            return "medium"
        elif score >= 0.40:
            return "low"
        else:
            return "very_low"
    
    def _interpret_score(self, score: float, source: str) -> str:
        """Generate human-readable interpretation of the score."""
        if score >= 0.85:
            return "High confidence - coordinates are likely accurate within a few kilometers"
        elif score >= 0.65:
            return f"Medium confidence - coordinates based on {source}, may be 5-15km off"
        elif score >= 0.40:
            return f"Low confidence - limited data available, coordinates are approximate"
        else:
            return "Very low confidence - insufficient data, coordinates are rough estimates only"


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_confidence(
    normalized: Dict,
    landmarks: List[Dict],
    geo_result: Dict,
    **kwargs
) -> Dict:
    """
    Convenience function to calculate confidence score.
    
    Args:
        normalized: Output from address normalization
        landmarks: List of extracted landmarks
        geo_result: Geocoding result
        **kwargs: Options passed to ConfidenceScorer
        
    Returns:
        Dict with score and breakdown
    """
    scorer = ConfidenceScorer(**kwargs)
    return scorer.score(normalized, landmarks, geo_result)
