"""
Contextual Geocoding for Indian Addresses.

Estimates geographic coordinates using multiple signals:
1. Pincode centroid lookup (most reliable)
2. State/city context resolution  
3. Landmark-aware refinement
4. External API fallback (Nominatim)

Design philosophy:
- Prefer local lookups over API calls (faster, no rate limits)
- Use hierarchical resolution (pincode > city > state > country)
- Provide uncertainty estimates with coordinates
- Cache results for repeated queries

This is a lightweight geocoder suitable for MVP - production systems
would use dedicated geocoding services like Google Maps, HERE, or Mapbox.
"""

import re
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from functools import lru_cache

# Optional imports for external geocoding
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

from .utils import (
    load_pincode_centroids,
    load_indian_states,
    is_within_india,
    validate_pincode,
    haversine_distance,
)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class GeoResult:
    """
    Geocoding result with coordinates and metadata.
    
    Attributes:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        source: How the coordinates were obtained
        precision: Estimated precision level
        uncertainty_km: Estimated error radius in kilometers
        raw_response: Original response from geocoding source
    """
    latitude: float
    longitude: float
    source: str  # "pincode", "city", "state", "api", "fallback"
    precision: str  # "exact", "street", "locality", "city", "state", "country"
    uncertainty_km: float
    raw_response: Optional[dict] = None
    
    @property
    def coordinates(self) -> Tuple[float, float]:
        """Return coordinates as (lat, lon) tuple."""
        return (self.latitude, self.longitude)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "coordinates": {"lat": self.latitude, "lon": self.longitude},
            "source": self.source,
            "precision": self.precision,
            "uncertainty_km": self.uncertainty_km,
        }


# =============================================================================
# STATIC FALLBACK DATA
# =============================================================================

# Major city coordinates for fallback geocoding
# These are rough city center coordinates
MAJOR_CITY_COORDS = {
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "surat": (21.1702, 72.8311),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "kanpur": (26.4499, 80.3319),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "thane": (19.2183, 72.9781),
    "bhopal": (23.2599, 77.4126),
    "visakhapatnam": (17.6868, 83.2185),
    "patna": (25.5941, 85.1376),
    "vadodara": (22.3072, 73.1812),
    "ghaziabad": (28.6692, 77.4538),
    "ludhiana": (30.9010, 75.8573),
    "agra": (27.1767, 78.0081),
    "nashik": (19.9975, 73.7898),
    "varanasi": (25.3176, 82.9739),
    "chandigarh": (30.7333, 76.7794),
    "gurugram": (28.4595, 77.0266),
    "gurgaon": (28.4595, 77.0266),
    "noida": (28.5355, 77.3910),
    "coimbatore": (11.0168, 76.9558),
    "kochi": (9.9312, 76.2673),
    "thiruvananthapuram": (8.5241, 76.9366),
    "mysuru": (12.2958, 76.6394),
    "mysore": (12.2958, 76.6394),
    "mangaluru": (12.9141, 74.8560),
    "mangalore": (12.9141, 74.8560),
    "vijayawada": (16.5062, 80.6480),
    "jodhpur": (26.2389, 73.0243),
    "udaipur": (24.5854, 73.7125),
    "amritsar": (31.6340, 74.8723),
    "guwahati": (26.1445, 91.7362),
    "bhubaneswar": (20.2961, 85.8245),
    "ranchi": (23.3441, 85.3096),
    "dehradun": (30.3165, 78.0322),
    "shimla": (31.1048, 77.1734),
}

# State centroid coordinates for fallback
STATE_CENTROIDS = {
    "MH": (19.6633, 75.3003),  # Maharashtra
    "DL": (28.6139, 77.2090),  # Delhi
    "KA": (15.3173, 75.7139),  # Karnataka
    "TN": (11.1271, 78.6569),  # Tamil Nadu
    "UP": (27.1303, 80.8597),  # Uttar Pradesh
    "GJ": (22.2587, 71.1924),  # Gujarat
    "RJ": (27.0238, 74.2179),  # Rajasthan
    "WB": (22.9868, 87.8550),  # West Bengal
    "AP": (15.9129, 79.7400),  # Andhra Pradesh
    "TS": (18.1124, 79.0193),  # Telangana
    "KL": (10.8505, 76.2711),  # Kerala
    "MP": (23.4733, 77.9479),  # Madhya Pradesh
    "BR": (25.0961, 85.3131),  # Bihar
    "PB": (31.1471, 75.3412),  # Punjab
    "HR": (29.0588, 76.0856),  # Haryana
    "OR": (20.9517, 85.0985),  # Odisha
    "JH": (23.6102, 85.2799),  # Jharkhand
    "CG": (21.2787, 81.8661),  # Chhattisgarh
    "UK": (30.0668, 79.0193),  # Uttarakhand
    "HP": (31.1048, 77.1734),  # Himachal Pradesh
    "AS": (26.2006, 92.9376),  # Assam
    "GA": (15.2993, 74.1240),  # Goa
}


# =============================================================================
# GEOCODER CLASS
# =============================================================================

class ContextualGeocoder:
    """
    Geocodes Indian addresses using multiple contextual signals.
    
    Geocoding hierarchy (most to least precise):
    1. Pincode lookup - ~5-10km accuracy
    2. Locality/landmark refinement - may improve if known
    3. City centroid - ~10-20km accuracy
    4. State centroid - ~100km+ accuracy
    5. External API (Nominatim) - variable accuracy
    6. Country centroid (India) - last resort
    
    The geocoder tries each method in order and returns
    the first successful result with uncertainty estimates.
    """
    
    def __init__(
        self,
        use_external_api: bool = False,  # Disabled by default
        api_timeout: int = 5,
        cache_size: int = 1000,
    ):
        """
        Initialize geocoder.
        
        Args:
            use_external_api: Whether to use Nominatim for fallback
            api_timeout: Timeout in seconds for API calls
            cache_size: LRU cache size for geocoding results
        """
        self.use_external_api = use_external_api and GEOPY_AVAILABLE
        self.api_timeout = api_timeout
        
        # Initialize external geocoder if enabled
        self._nominatim = None
        if self.use_external_api:
            self._nominatim = Nominatim(
                user_agent="indian_address_geocoder_mvp",
                timeout=api_timeout
            )
        
        # Load static data
        self._pincode_coords = load_pincode_centroids()
        self._states = load_indian_states()
    
    def geocode(
        self,
        normalized_text: str,
        pincode: Optional[str] = None,
        landmarks: Optional[List[Dict]] = None,
        state_hint: Optional[str] = None,
        city_hint: Optional[str] = None,
    ) -> Dict:
        """
        Geocode an address using all available context.
        
        Args:
            normalized_text: Normalized address text
            pincode: Extracted pincode (if available)
            landmarks: Extracted landmarks (if available)
            state_hint: Known state code (if available)
            city_hint: Known city name (if available)
            
        Returns:
            Dict with coordinates, source, and uncertainty
        """
        # Try geocoding methods in order of precision
        
        # Method 1: Pincode lookup (most precise for Indian addresses)
        if pincode and validate_pincode(pincode):
            result = self._geocode_by_pincode(pincode)
            if result:
                return result.to_dict()
        
        # Method 2: City lookup from hint or text
        city = city_hint or self._extract_city_from_text(normalized_text)
        if city:
            result = self._geocode_by_city(city)
            if result:
                return result.to_dict()
        
        # Method 3: State centroid
        state = state_hint or self._extract_state_from_text(normalized_text)
        if state:
            result = self._geocode_by_state(state)
            if result:
                return result.to_dict()
        
        # Method 4: External API (if enabled)
        if self.use_external_api:
            result = self._geocode_by_api(normalized_text)
            if result:
                return result.to_dict()
        
        # Method 5: Country fallback (center of India)
        return self._get_india_fallback().to_dict()
    
    def _geocode_by_pincode(self, pincode: str) -> Optional[GeoResult]:
        """
        Look up coordinates by pincode.
        
        Pincodes typically cover areas of 5-15 km radius,
        so we return centroid with corresponding uncertainty.
        """
        coords = self._pincode_coords.get(pincode)
        
        if coords:
            return GeoResult(
                latitude=coords[0],
                longitude=coords[1],
                source="pincode",
                precision="locality",
                uncertainty_km=5.0,  # Typical pincode area radius
            )
        
        # Try to infer from pincode prefix (less precise)
        # First 3 digits indicate a broader region
        if len(pincode) >= 3:
            prefix = pincode[:3]
            for pc, coord in self._pincode_coords.items():
                if pc.startswith(prefix):
                    return GeoResult(
                        latitude=coord[0],
                        longitude=coord[1],
                        source="pincode_prefix",
                        precision="city",
                        uncertainty_km=20.0,  # Less precise
                    )
        
        return None
    
    def _geocode_by_city(self, city: str) -> Optional[GeoResult]:
        """Look up coordinates by city name."""
        city_lower = city.lower().strip()
        
        coords = MAJOR_CITY_COORDS.get(city_lower)
        if coords:
            return GeoResult(
                latitude=coords[0],
                longitude=coords[1],
                source="city",
                precision="city",
                uncertainty_km=15.0,  # City center, could be anywhere in city
            )
        
        return None
    
    def _geocode_by_state(self, state_code: str) -> Optional[GeoResult]:
        """Look up coordinates by state code."""
        coords = STATE_CENTROIDS.get(state_code.upper())
        
        if coords:
            return GeoResult(
                latitude=coords[0],
                longitude=coords[1],
                source="state",
                precision="state",
                uncertainty_km=150.0,  # State centroid, very imprecise
            )
        
        return None
    
    def _geocode_by_api(self, address: str) -> Optional[GeoResult]:
        """
        Geocode using external Nominatim API.
        
        This is a fallback for addresses that don't match our static data.
        Rate limited and may be slow, so we prefer local lookups.
        """
        if not self._nominatim:
            return None
        
        try:
            # Add India to query for better results
            query = f"{address}, India"
            location = self._nominatim.geocode(query, country_codes="in")
            
            if location:
                lat, lon = location.latitude, location.longitude
                
                # Validate the result is actually in India
                if not is_within_india(lat, lon):
                    return None
                
                # Determine precision from Nominatim response
                precision = self._estimate_api_precision(location.raw)
                
                return GeoResult(
                    latitude=lat,
                    longitude=lon,
                    source="nominatim",
                    precision=precision,
                    uncertainty_km=self._uncertainty_for_precision(precision),
                    raw_response=location.raw,
                )
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            # API errors are expected, just fall through
            pass
        except Exception as e:
            # Unexpected errors - log but don't crash
            print(f"Geocoding API error: {e}")
        
        return None
    
    def _estimate_api_precision(self, raw_response: dict) -> str:
        """Estimate precision level from Nominatim response."""
        if not raw_response:
            return "locality"
        
        # Nominatim includes a 'type' field that indicates result granularity
        result_type = raw_response.get("type", "")
        address_type = raw_response.get("addresstype", "")
        
        precision_map = {
            "house": "exact",
            "building": "exact",
            "street": "street",
            "neighbourhood": "locality",
            "suburb": "locality",
            "city": "city",
            "town": "city",
            "village": "city",
            "state": "state",
            "country": "country",
        }
        
        return precision_map.get(result_type, precision_map.get(address_type, "locality"))
    
    def _uncertainty_for_precision(self, precision: str) -> float:
        """Map precision level to uncertainty radius in km."""
        uncertainty_map = {
            "exact": 0.1,
            "street": 0.5,
            "locality": 2.0,
            "city": 10.0,
            "state": 100.0,
            "country": 500.0,
        }
        return uncertainty_map.get(precision, 10.0)
    
    def _extract_city_from_text(self, text: str) -> Optional[str]:
        """Try to identify city from address text."""
        text_lower = text.lower()
        
        for city in MAJOR_CITY_COORDS.keys():
            if city in text_lower:
                return city
        
        return None
    
    def _extract_state_from_text(self, text: str) -> Optional[str]:
        """Try to identify state from address text."""
        text_lower = text.lower()
        
        for code, info in self._states.items():
            if info["name"].lower() in text_lower:
                return code
            for alias in info.get("aliases", []):
                if f" {alias.lower()} " in f" {text_lower} ":
                    return code
        
        return None
    
    def _get_india_fallback(self) -> GeoResult:
        """Return center of India as last-resort fallback."""
        # Geographic center of India (approximately)
        return GeoResult(
            latitude=20.5937,
            longitude=78.9629,
            source="country_fallback",
            precision="country",
            uncertainty_km=1500.0,  # Very imprecise
        )


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def geocode_address(
    address: str,
    pincode: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Convenience function to geocode an address.
    
    Args:
        address: Address text (ideally normalized)
        pincode: Known pincode (optional)
        **kwargs: Options passed to ContextualGeocoder
        
    Returns:
        Dict with coordinates and metadata
    """
    geocoder = ContextualGeocoder(**kwargs)
    return geocoder.geocode(
        normalized_text=address,
        pincode=pincode,
    )
