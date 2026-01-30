# Geospatial NLP Package for Indian Address Processing
# Exposes main processing functions for backend integration

from .normalizer import AddressNormalizer, normalize_address
from .landmark_extractor import LandmarkExtractor, extract_landmarks
from .geocoder import ContextualGeocoder, geocode_address
from .confidence import ConfidenceScorer, calculate_confidence
from .data_loader import DataLoader, get_data_loader

__version__ = "0.1.0"
__all__ = [
    "AddressNormalizer",
    "normalize_address",
    "LandmarkExtractor", 
    "extract_landmarks",
    "ContextualGeocoder",
    "geocode_address",
    "ConfidenceScorer",
    "calculate_confidence",
    "DataLoader",
    "get_data_loader",
    "process_address",
]


def process_address(raw_address: str, config: dict = None) -> dict:
    """
    Main entry point for address processing pipeline.
    
    Orchestrates normalization → landmark extraction → geocoding → confidence scoring.
    
    Args:
        raw_address: Messy, informal Indian address text
        config: Optional configuration overrides
        
    Returns:
        dict with keys: normalized_address, landmarks, coordinates, confidence
    """
    config = config or {}
    
    # Step 1: Normalize the raw address
    normalizer = AddressNormalizer()
    normalized = normalizer.normalize(raw_address)
    
    # Step 2: Extract landmarks from normalized text
    extractor = LandmarkExtractor()
    landmarks = extractor.extract(normalized["text"])
    
    # Step 3: Geocode using all available context
    geocoder = ContextualGeocoder()
    geo_result = geocoder.geocode(
        normalized_text=normalized["text"],
        pincode=normalized.get("pincode"),
        landmarks=landmarks,
        state_hint=normalized.get("state")
    )
    
    # Step 4: Calculate confidence score
    scorer = ConfidenceScorer()
    confidence = scorer.score(
        normalized=normalized,
        landmarks=landmarks,
        geo_result=geo_result
    )
    
    return {
        "raw_address": raw_address,
        "normalized_address": normalized["text"],
        "pincode": normalized.get("pincode"),
        "state": normalized.get("state"),
        "city": normalized.get("city"),
        "landmarks": landmarks,
        "coordinates": geo_result.get("coordinates"),
        "geo_source": geo_result.get("source"),
        "confidence": confidence,
    }
