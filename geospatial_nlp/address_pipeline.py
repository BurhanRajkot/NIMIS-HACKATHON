"""
Address Pipeline - End-to-End Address Processing.

Orchestrates the full address processing pipeline:
1. Address normalization
2. Landmark matching
3. Location prediction
4. Confidence scoring

Designed for backend integration - no UI code.
Returns structured JSON-serializable output.

Usage:
    from geospatial_nlp.address_pipeline import process_address
    
    result = process_address("near hanuman temple, 2nd gali", city="indore")
    print(result["predicted_coordinates"])
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time

# Import pipeline components
from .address_normalizer import normalize_address
from .landmark_matcher import match_landmark, get_matcher, build_landmark_embeddings
from .location_predictor import predict_location
from .confidence_scorer import score_confidence


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PipelineResult:
    """
    Complete result from address processing pipeline.
    
    All fields are JSON-serializable for API responses.
    """
    # Input
    raw_address: str
    city: Optional[str]
    
    # Normalization output
    standardized_address: str
    extracted_landmarks: List[Dict]
    directions: List[str]
    street_info: Dict
    
    # Matching output
    matched_landmarks: List[Dict]
    
    # Prediction output
    predicted_coordinates: Dict
    
    # Confidence output
    confidence: Dict
    
    # Metadata
    processing_time_ms: float = 0.0
    pipeline_version: str = "1.0.0"
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "raw_address": self.raw_address,
            "city": self.city,
            "standardized_address": self.standardized_address,
            "extracted_landmarks": self.extracted_landmarks,
            "directions": self.directions,
            "street_info": self.street_info,
            "matched_landmarks": self.matched_landmarks,
            "predicted_coordinates": self.predicted_coordinates,
            "confidence": self.confidence,
            "metadata": {
                "processing_time_ms": round(self.processing_time_ms, 2),
                "pipeline_version": self.pipeline_version,
            }
        }


# =============================================================================
# PIPELINE CLASS
# =============================================================================

class AddressPipeline:
    """
    End-to-end address processing pipeline.
    
    Orchestrates:
    1. Address normalization (text cleaning, abbreviation expansion)
    2. Landmark matching (semantic similarity to POI database)
    3. Location prediction (coordinate estimation from landmarks)
    4. Confidence scoring (reliability assessment)
    
    Thread-safe and stateless per request.
    """
    
    def __init__(
        self,
        data_path: Optional[str] = None,
        use_embeddings: bool = True,
        preload_embeddings: bool = False,
    ):
        """
        Initialize pipeline.
        
        Args:
            data_path: Path to data directory with landmarks.csv
            use_embeddings: Use semantic embeddings for matching
            preload_embeddings: Build embeddings at init (recommended for production)
        """
        self.data_path = data_path
        self.use_embeddings = use_embeddings
        self._initialized = False
        
        if preload_embeddings:
            self._initialize_matcher()
    
    def _initialize_matcher(self):
        """Initialize landmark matcher with embeddings."""
        if not self._initialized:
            try:
                build_landmark_embeddings(
                    data_path=self.data_path,
                )
                self._initialized = True
            except Exception as e:
                print(f"Warning: Failed to initialize embeddings: {e}")
    
    def process(
        self,
        raw_address: str,
        city: Optional[str] = None,
        nlp_confidence: float = 0.8,  # Mock for now
        density_score: float = 0.7,   # Simulated for now
    ) -> Dict:
        """
        Process an address through the full pipeline.
        
        Args:
            raw_address: Raw messy address text
            city: City name for landmark filtering (optional but recommended)
            nlp_confidence: NLP extraction confidence (mock value)
            density_score: Delivery density in area (simulated)
            
        Returns:
            Complete pipeline result as dictionary
            
        Example:
            >>> pipeline = AddressPipeline()
            >>> result = pipeline.process(
            ...     "near hanuman temple, 2nd gali",
            ...     city="indore"
            ... )
            >>> print(result["predicted_coordinates"])
        """
        start_time = time.time()
        
        # Ensure matcher is initialized
        if not self._initialized:
            self._initialize_matcher()
        
        # =====================================================================
        # STEP 1: Address Normalization
        # =====================================================================
        normalized = normalize_address(raw_address)
        
        standardized_address = normalized.get("clean_text", "")
        extracted_landmarks = normalized.get("landmarks", [])
        directions = normalized.get("directions", [])
        street_info = normalized.get("street_info", {})
        
        # =====================================================================
        # STEP 2: Landmark Matching
        # =====================================================================
        matched_landmarks = []
        
        # Match each extracted landmark phrase
        for landmark in extracted_landmarks:
            phrase = landmark.get("landmark", landmark.get("phrase", ""))
            if phrase:
                matches = match_landmark(phrase, city=city, top_k=1)
                if matches:
                    matched_landmarks.extend(matches)
        
        # If no landmarks extracted, try matching the whole normalized text
        if not matched_landmarks and standardized_address:
            # Extract potential landmark from text
            words = standardized_address.split()
            # Try matching 2-3 word chunks
            for i in range(len(words) - 1):
                chunk = " ".join(words[i:i+2])
                matches = match_landmark(chunk, city=city, top_k=1)
                if matches and matches[0].get("similarity", 0) > 0.6:
                    matched_landmarks.extend(matches)
                    break
        
        # =====================================================================
        # STEP 3: Location Prediction
        # =====================================================================
        address_components = {
            "landmarks": extracted_landmarks,
            "directions": directions,
            "street_info": street_info,
        }
        
        predicted_coords = predict_location(
            matched_landmarks=matched_landmarks,
            address_components=address_components,
        )
        
        # =====================================================================
        # STEP 4: Confidence Scoring
        # =====================================================================
        landmark_scores = [
            lm.get("similarity", 0.5) 
            for lm in matched_landmarks
        ]
        
        geo_features = {
            "directions": directions,
            "landmarks": extracted_landmarks,
            "street_info": street_info,
            "distance_m": predicted_coords.get("offset_applied_m", 100),
        }
        
        confidence = score_confidence(
            nlp_conf=nlp_confidence,
            landmark_scores=landmark_scores,
            geo_features=geo_features,
            density_score=density_score,
        )
        
        # =====================================================================
        # STEP 5: Build Response
        # =====================================================================
        processing_time_ms = (time.time() - start_time) * 1000
        
        result = PipelineResult(
            raw_address=raw_address,
            city=city,
            standardized_address=standardized_address,
            extracted_landmarks=extracted_landmarks,
            directions=directions,
            street_info=street_info,
            matched_landmarks=matched_landmarks,
            predicted_coordinates={
                "lat": predicted_coords.get("lat"),
                "lng": predicted_coords.get("lng"),
                "anchor_landmark": predicted_coords.get("anchor_landmark"),
                "method": predicted_coords.get("method"),
            },
            confidence={
                "score": confidence.get("confidence_score"),
                "level": confidence.get("confidence_level"),
                "interpretation": confidence.get("interpretation"),
            },
            processing_time_ms=processing_time_ms,
        )
        
        return result.to_dict()


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTION
# =============================================================================

# Global pipeline instance
_global_pipeline: Optional[AddressPipeline] = None


def get_pipeline(**kwargs) -> AddressPipeline:
    """Get or create global pipeline instance."""
    global _global_pipeline
    
    if _global_pipeline is None:
        _global_pipeline = AddressPipeline(**kwargs)
    
    return _global_pipeline


def process_address(
    raw_address: str,
    city: Optional[str] = None,
    **kwargs,
) -> Dict:
    """
    Process an address through the full pipeline.
    
    This is the main entry point for backend integration.
    
    Args:
        raw_address: Raw messy address text
        city: City name for better landmark matching
        **kwargs: Additional options (nlp_confidence, density_score)
        
    Returns:
        Complete pipeline result:
        {
            "standardized_address": "...",
            "matched_landmarks": [...],
            "predicted_coordinates": {"lat": ..., "lng": ...},
            "confidence": {"score": ..., "level": ...}
        }
        
    Example:
        >>> result = process_address(
        ...     "near hanuman temple, 2nd gali, behind station",
        ...     city="indore"
        ... )
        >>> print(f"Coordinates: ({result['predicted_coordinates']['lat']}, "
        ...       f"{result['predicted_coordinates']['lng']})")
        >>> print(f"Confidence: {result['confidence']['level']}")
    """
    pipeline = get_pipeline()
    return pipeline.process(raw_address, city=city, **kwargs)


def initialize_pipeline(data_path: Optional[str] = None, preload: bool = True):
    """
    Initialize the pipeline with embeddings.
    
    Call this once at server startup for better performance.
    
    Args:
        data_path: Path to data directory
        preload: Whether to preload embeddings
    """
    global _global_pipeline
    _global_pipeline = AddressPipeline(
        data_path=data_path,
        preload_embeddings=preload,
    )
    return _global_pipeline


# =============================================================================
# BATCH PROCESSING
# =============================================================================

def process_batch(
    addresses: List[Dict],
    default_city: Optional[str] = None,
) -> List[Dict]:
    """
    Process multiple addresses in batch.
    
    Args:
        addresses: List of dicts with 'address' and optional 'city' keys
        default_city: Default city if not specified per address
        
    Returns:
        List of pipeline results
        
    Example:
        >>> addresses = [
        ...     {"address": "near temple, 1st gali", "city": "mumbai"},
        ...     {"address": "opp station, main road", "city": "delhi"},
        ... ]
        >>> results = process_batch(addresses)
    """
    pipeline = get_pipeline()
    results = []
    
    for item in addresses:
        if isinstance(item, str):
            address = item
            city = default_city
        else:
            address = item.get("address", item.get("raw_address", ""))
            city = item.get("city", default_city)
        
        result = pipeline.process(address, city=city)
        results.append(result)
    
    return results


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("Address Pipeline Demo")
    print("=" * 60)
    
    # Test addresses
    test_cases = [
        {
            "address": "near hanuman temple, 2nd gali, behind station",
            "city": "indore",
        },
        {
            "address": "opp city hospital, main road, nr railway station",
            "city": "mumbai",
        },
        {
            "address": "beside big market, 3rd lane, andheri east",
            "city": "mumbai",
        },
    ]
    
    print("\nProcessing addresses...\n")
    
    for i, case in enumerate(test_cases):
        print(f"--- Address {i+1} ---")
        print(f"Input: {case['address']}")
        print(f"City: {case['city']}")
        
        result = process_address(case["address"], city=case["city"])
        
        print(f"\nStandardized: {result['standardized_address']}")
        print(f"Matched Landmarks: {len(result['matched_landmarks'])}")
        
        if result['matched_landmarks']:
            for lm in result['matched_landmarks']:
                print(f"  - {lm.get('matched_name', 'N/A')} (sim: {lm.get('similarity', 0):.2f})")
        
        coords = result['predicted_coordinates']
        if coords.get('lat'):
            print(f"Predicted: ({coords['lat']:.6f}, {coords['lng']:.6f})")
            print(f"Method: {coords.get('method', 'N/A')}")
        
        conf = result['confidence']
        print(f"Confidence: {conf['score']:.2f} ({conf['level']})")
        print(f"Time: {result['metadata']['processing_time_ms']:.1f}ms")
        print()
