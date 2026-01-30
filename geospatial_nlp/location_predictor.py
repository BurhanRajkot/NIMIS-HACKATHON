"""
Location Predictor Module for Indian Address Geocoding.

Predicts final delivery coordinates using:
- Matched landmark coordinates (anchor point)
- Relative direction words (near, behind, after)
- Lane/street numbers for distance estimation

Approach: Rule-based spatial logic (MVP)
- Easy to understand and debug
- Can be replaced with ML model later
- Uses haversine-based coordinate offsets

ML Notes:
- This module is designed to be replaceable with a learned model
- The predict_location() function signature is stable
- anchor_point in output provides explainability
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


# =============================================================================
# CONSTANTS
# =============================================================================

# Earth's radius in meters
EARTH_RADIUS_M = 6371000

# Direction offsets (approximate bearings in degrees from north)
# Used when direction word implies spatial relationship
DIRECTION_BEARINGS = {
    "north": 0,
    "northeast": 45,
    "east": 90,
    "southeast": 135,
    "south": 180,
    "southwest": 225,
    "west": 270,
    "northwest": 315,
}

# Direction word to bearing mapping (for relative positioning)
# These are approximate - real logic would need context
RELATIVE_DIRECTION_CONFIG = {
    # "near" → random bearing, small offset (50-100m)
    "near": {
        "min_offset_m": 50,
        "max_offset_m": 100,
        "bearing_mode": "random",  # Random direction
    },
    # "behind" → opposite direction (180°), medium offset
    "behind": {
        "min_offset_m": 30,
        "max_offset_m": 80,
        "bearing_mode": "opposite",  # Opposite of assumed front
        "base_bearing": 180,
    },
    # "opposite" → across the street/road, small offset
    "opposite": {
        "min_offset_m": 20,
        "max_offset_m": 50,
        "bearing_mode": "opposite",
        "base_bearing": 180,
    },
    # "beside" / "adjacent" → perpendicular, small offset
    "beside": {
        "min_offset_m": 10,
        "max_offset_m": 40,
        "bearing_mode": "perpendicular",
        "base_bearing": 90,
    },
    "adjacent": {
        "min_offset_m": 10,
        "max_offset_m": 40,
        "bearing_mode": "perpendicular",
        "base_bearing": 90,
    },
    # "after" / "past" → forward along path
    "after": {
        "min_offset_m": 100,
        "max_offset_m": 200,
        "bearing_mode": "forward",
        "base_bearing": 0,
    },
    "past": {
        "min_offset_m": 100,
        "max_offset_m": 200,
        "bearing_mode": "forward",
        "base_bearing": 0,
    },
    # "before" → backward along path
    "before": {
        "min_offset_m": 100,
        "max_offset_m": 200,
        "bearing_mode": "backward",
        "base_bearing": 180,
    },
    # "next to" → very close
    "next to": {
        "min_offset_m": 5,
        "max_offset_m": 30,
        "bearing_mode": "random",
    },
    # "in front of" → facing the landmark
    "in front of": {
        "min_offset_m": 15,
        "max_offset_m": 50,
        "bearing_mode": "fixed",
        "base_bearing": 0,
    },
    # "across from" → opposite side
    "across from": {
        "min_offset_m": 30,
        "max_offset_m": 80,
        "bearing_mode": "opposite",
        "base_bearing": 180,
    },
}

# Lane number to additional offset (larger lane number = further)
LANE_OFFSET_MULTIPLIER = 15  # meters per lane number


# =============================================================================
# GEOSPATIAL UTILITIES
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in meters.
    
    Uses the Haversine formula for accuracy on spherical Earth.
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS_M * c


def offset_coordinate(
    lat: float,
    lon: float,
    bearing_deg: float,
    distance_m: float,
) -> Tuple[float, float]:
    """
    Calculate new coordinate given start point, bearing, and distance.
    
    Args:
        lat: Starting latitude
        lon: Starting longitude
        bearing_deg: Bearing in degrees (0 = north, 90 = east)
        distance_m: Distance to offset in meters
        
    Returns:
        Tuple of (new_lat, new_lon)
        
    ML Note: This is the core function for spatial prediction.
    A learned model could predict (bearing, distance) directly
    instead of using rule-based logic.
    """
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_deg)
    
    # Angular distance
    angular_dist = distance_m / EARTH_RADIUS_M
    
    # Calculate new latitude
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_dist) +
        math.cos(lat_rad) * math.sin(angular_dist) * math.cos(bearing_rad)
    )
    
    # Calculate new longitude
    new_lon_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_dist) * math.cos(lat_rad),
        math.cos(angular_dist) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    
    return (math.degrees(new_lat_rad), math.degrees(new_lon_rad))


def random_bearing() -> float:
    """Generate random bearing (0-360 degrees)."""
    return random.uniform(0, 360)


# =============================================================================
# PREDICTION LOGIC
# =============================================================================

@dataclass
class PredictionResult:
    """
    Result of location prediction.
    
    Contains predicted coordinates and metadata for transparency.
    """
    lat: float
    lng: float
    confidence: float
    anchor_landmark: Optional[Dict]
    direction_used: Optional[str]
    offset_applied_m: float
    bearing_applied_deg: float
    method: str  # "landmark_offset", "landmark_direct", "fallback"
    
    def to_dict(self) -> Dict:
        return {
            "lat": round(self.lat, 6),
            "lng": round(self.lng, 6),
            "confidence": round(self.confidence, 3),
            "anchor_landmark": self.anchor_landmark,
            "direction_used": self.direction_used,
            "offset_applied_m": round(self.offset_applied_m, 1),
            "bearing_applied_deg": round(self.bearing_applied_deg, 1),
            "method": self.method,
        }


class LocationPredictor:
    """
    Predicts delivery coordinates using landmarks and spatial logic.
    
    Pipeline:
    1. Select best anchor landmark from matched landmarks
    2. Determine offset direction from address components
    3. Calculate offset distance based on direction + lane number
    4. Apply geographic offset to get final coordinates
    
    ML Notes:
    - This class uses rule-based logic for MVP
    - The predict() method can be overridden by a subclass with ML model
    - anchor_landmark in output provides explainability
    """
    
    def __init__(
        self,
        default_offset_m: float = 75,
        lane_multiplier: float = LANE_OFFSET_MULTIPLIER,
        seed: int = None,
    ):
        """
        Initialize location predictor.
        
        Args:
            default_offset_m: Default offset when no direction specified
            lane_multiplier: Meters to add per lane number
            seed: Random seed for reproducibility
        """
        self.default_offset_m = default_offset_m
        self.lane_multiplier = lane_multiplier
        
        if seed is not None:
            random.seed(seed)
    
    def predict(
        self,
        matched_landmarks: List[Dict],
        address_components: Dict,
    ) -> Dict:
        """
        Predict delivery location from landmarks and address components.
        
        Args:
            matched_landmarks: List of matched landmark dicts with lat/lng
            address_components: Dict with directions, street_info, etc.
            
        Returns:
            PredictionResult as dictionary
            
        ML Note: This is the main interface. A learned model would:
        1. Take same inputs
        2. Return same output format
        3. Replace rule-based logic with neural network inference
        """
        # Handle empty input
        if not matched_landmarks:
            return self._fallback_prediction(address_components)
        
        # Step 1: Select anchor landmark (highest similarity)
        anchor = self._select_anchor(matched_landmarks)
        
        if not anchor or "lat" not in anchor:
            return self._fallback_prediction(address_components)
        
        # Step 2: Get direction from address components
        direction = self._get_primary_direction(address_components)
        
        # Step 3: Calculate offset parameters
        bearing, distance = self._calculate_offset(
            direction=direction,
            address_components=address_components,
        )
        
        # Step 4: Apply offset to anchor coordinates
        new_lat, new_lng = offset_coordinate(
            lat=anchor["lat"],
            lon=anchor.get("lng", anchor.get("lon", anchor.get("longitude", 0))),
            bearing_deg=bearing,
            distance_m=distance,
        )
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(
            anchor=anchor,
            direction=direction,
            address_components=address_components,
        )
        
        return PredictionResult(
            lat=new_lat,
            lng=new_lng,
            confidence=confidence,
            anchor_landmark=anchor,
            direction_used=direction,
            offset_applied_m=distance,
            bearing_applied_deg=bearing,
            method="landmark_offset" if direction else "landmark_direct",
        ).to_dict()
    
    def _select_anchor(self, matched_landmarks: List[Dict]) -> Optional[Dict]:
        """
        Select the best landmark to use as anchor point.
        
        Selection criteria:
        1. Highest similarity score
        2. Has valid coordinates
        
        ML Note: Could be extended to consider:
        - Landmark type (e.g., prefer buildings over areas)
        - Distance between multiple landmarks for validation
        """
        valid_landmarks = [
            lm for lm in matched_landmarks
            if lm.get("lat") is not None and lm.get("similarity", 0) > 0
        ]
        
        if not valid_landmarks:
            # Try alternate key names
            valid_landmarks = [
                lm for lm in matched_landmarks
                if lm.get("latitude") is not None
            ]
            # Normalize key names
            for lm in valid_landmarks:
                if "latitude" in lm:
                    lm["lat"] = lm["latitude"]
                if "longitude" in lm:
                    lm["lng"] = lm["longitude"]
        
        if not valid_landmarks:
            return None
        
        # Sort by similarity descending
        return max(valid_landmarks, key=lambda x: x.get("similarity", 0.5))
    
    def _get_primary_direction(self, address_components: Dict) -> Optional[str]:
        """
        Extract primary direction word from address components.
        
        Returns the first direction that has a defined offset config.
        """
        directions = address_components.get("directions", [])
        
        for direction in directions:
            direction_lower = direction.lower()
            if direction_lower in RELATIVE_DIRECTION_CONFIG:
                return direction_lower
        
        # Check landmarks for embedded direction
        landmarks = address_components.get("landmarks", [])
        for lm in landmarks:
            lm_direction = lm.get("direction", "").lower()
            if lm_direction in RELATIVE_DIRECTION_CONFIG:
                return lm_direction
        
        return None
    
    def _calculate_offset(
        self,
        direction: Optional[str],
        address_components: Dict,
    ) -> Tuple[float, float]:
        """
        Calculate bearing and distance for offset.
        
        Uses direction word and lane number to determine offset.
        
        Returns:
            Tuple of (bearing_degrees, distance_meters)
        """
        # Get lane number adjustment
        lane_offset = 0
        street_info = address_components.get("street_info", {})
        street_numbers = street_info.get("street_numbers", [])
        
        if street_numbers:
            # Use first lane number found
            try:
                lane_num = int(street_numbers[0].get("number", 0))
                lane_offset = lane_num * self.lane_multiplier
            except (ValueError, TypeError):
                pass
        
        # Get direction-based offset
        if direction and direction in RELATIVE_DIRECTION_CONFIG:
            config = RELATIVE_DIRECTION_CONFIG[direction]
            
            # Calculate distance
            min_offset = config["min_offset_m"]
            max_offset = config["max_offset_m"]
            base_distance = random.uniform(min_offset, max_offset)
            total_distance = base_distance + lane_offset
            
            # Calculate bearing
            bearing_mode = config["bearing_mode"]
            if bearing_mode == "random":
                bearing = random_bearing()
            elif bearing_mode in ("opposite", "backward"):
                bearing = config.get("base_bearing", 180)
                # Add some randomness (±30 degrees)
                bearing += random.uniform(-30, 30)
            elif bearing_mode == "perpendicular":
                # Choose left or right randomly
                bearing = config.get("base_bearing", 90)
                if random.random() > 0.5:
                    bearing = 360 - bearing
            elif bearing_mode == "forward":
                bearing = config.get("base_bearing", 0)
                bearing += random.uniform(-20, 20)
            else:  # fixed
                bearing = config.get("base_bearing", 0)
            
            return (bearing % 360, total_distance)
        
        # Default: random direction, default offset
        return (random_bearing(), self.default_offset_m + lane_offset)
    
    def _calculate_confidence(
        self,
        anchor: Dict,
        direction: Optional[str],
        address_components: Dict,
    ) -> float:
        """
        Calculate confidence score for prediction.
        
        Factors:
        - Anchor landmark similarity
        - Presence of direction word
        - Presence of lane/building number
        """
        # Start with anchor similarity
        base_confidence = anchor.get("similarity", 0.5)
        
        # Direction word bonus
        if direction:
            base_confidence += 0.1
        
        # Lane/building number bonus
        street_info = address_components.get("street_info", {})
        if street_info.get("street_numbers"):
            base_confidence += 0.05
        if street_info.get("building_numbers"):
            base_confidence += 0.05
        
        # Multiple landmarks for cross-validation bonus
        landmarks = address_components.get("landmarks", [])
        if len(landmarks) >= 2:
            base_confidence += 0.05
        
        return min(base_confidence, 0.95)
    
    def _fallback_prediction(self, address_components: Dict) -> Dict:
        """
        Fallback when no landmarks available.
        
        Returns empty prediction with low confidence.
        """
        return PredictionResult(
            lat=0.0,
            lng=0.0,
            confidence=0.0,
            anchor_landmark=None,
            direction_used=None,
            offset_applied_m=0,
            bearing_applied_deg=0,
            method="fallback",
        ).to_dict()


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTION
# =============================================================================

# Global predictor instance
_global_predictor: Optional[LocationPredictor] = None


def get_predictor(**kwargs) -> LocationPredictor:
    """Get or create global predictor instance."""
    global _global_predictor
    
    if _global_predictor is None:
        _global_predictor = LocationPredictor(**kwargs)
    
    return _global_predictor


def predict_location(
    matched_landmarks: List[Dict],
    address_components: Dict,
    **kwargs,
) -> Dict:
    """
    Predict final delivery coordinates.
    
    Args:
        matched_landmarks: List of matched landmark dicts from LandmarkMatcher
            Expected format: {"lat": ..., "lng": ..., "similarity": ..., ...}
        address_components: Output from extract_address_components()
            Expected format: {"landmarks": [...], "directions": [...], "street_info": {...}}
        **kwargs: Additional options for LocationPredictor
        
    Returns:
        Dict with predicted coordinates and metadata:
        {
            "lat": 22.7201,
            "lng": 75.8589,
            "confidence": 0.82,
            "anchor_landmark": {...},
            "direction_used": "near",
            "offset_applied_m": 75.5,
            "bearing_applied_deg": 145.2,
            "method": "landmark_offset"
        }
        
    Example:
        >>> landmarks = [{"lat": 22.7201, "lng": 75.8589, "similarity": 0.87}]
        >>> components = {"directions": ["near"], "street_info": {"street_numbers": [{"number": "2"}]}}
        >>> result = predict_location(landmarks, components)
        >>> print(f"Delivery at: ({result['lat']}, {result['lng']})")
    """
    predictor = get_predictor(**kwargs) if kwargs else get_predictor()
    return predictor.predict(matched_landmarks, address_components)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("Location Predictor Demo")
    print("=" * 50)
    
    # Test data
    matched_landmarks = [
        {
            "input_landmark": "big temple",
            "matched_name": "Hanuman Mandir",
            "lat": 22.7201,
            "lng": 75.8589,
            "similarity": 0.87,
        }
    ]
    
    test_cases = [
        {"directions": ["near"], "street_info": {}},
        {"directions": ["behind"], "street_info": {"street_numbers": [{"number": "2"}]}},
        {"directions": ["opposite"], "street_info": {}},
        {"directions": ["after"], "street_info": {"street_numbers": [{"number": "5"}]}},
    ]
    
    print("\nAnchor Landmark: Hanuman Mandir (22.7201, 75.8589)")
    print("-" * 50)
    
    predictor = LocationPredictor(seed=42)  # Fixed seed for reproducibility
    
    for i, components in enumerate(test_cases):
        result = predictor.predict(matched_landmarks, components)
        
        direction = components["directions"][0] if components["directions"] else "none"
        lane = components["street_info"].get("street_numbers", [{}])
        lane_num = lane[0].get("number", "-") if lane else "-"
        
        print(f"\n{i+1}. Direction: '{direction}', Lane: {lane_num}")
        print(f"   Predicted: ({result['lat']:.6f}, {result['lng']:.6f})")
        print(f"   Offset: {result['offset_applied_m']:.1f}m @ {result['bearing_applied_deg']:.1f}°")
        print(f"   Confidence: {result['confidence']:.2f}")
