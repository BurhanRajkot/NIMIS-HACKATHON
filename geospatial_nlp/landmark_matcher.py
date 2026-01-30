"""
Landmark Matcher Module for Indian Addresses.

Uses semantic embeddings to match user-extracted landmark phrases
to actual POIs (Points of Interest) from the landmarks dataset.

Approach:
1. Load landmarks from CSV dataset
2. Build embeddings using lightweight sentence-transformers model
3. Compute cosine similarity for matching
4. Return best matches with coordinates

ML Notes:
- Uses 'all-MiniLM-L6-v2' (22MB) - fast and good for semantic similarity
- Falls back to fuzzy string matching if sentence-transformers unavailable
- Embeddings are cached for performance
- City filtering reduces search space for faster matching
"""

import csv
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from functools import lru_cache

# Conditional imports for ML dependencies
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Landmark:
    """
    Represents a landmark from the dataset.
    
    Schema matches landmarks.csv:
    - name: Landmark name
    - type: Category (temple, hospital, etc.)
    - latitude: Latitude coordinate
    - longitude: Longitude coordinate  
    - city: City where landmark is located
    """
    name: str
    type: str
    latitude: float
    longitude: float
    city: str
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "lat": self.latitude,
            "lng": self.longitude,
            "city": self.city,
        }


@dataclass
class MatchResult:
    """
    Result of landmark matching.
    
    Contains the input phrase, matched landmark, and similarity score.
    """
    input_landmark: str
    matched_name: str
    lat: float
    lng: float
    similarity: float
    landmark_type: Optional[str] = None
    city: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "input_landmark": self.input_landmark,
            "matched_name": self.matched_name,
            "lat": self.lat,
            "lng": self.lng,
            "similarity": round(self.similarity, 4),
            "type": self.landmark_type,
            "city": self.city,
        }


# =============================================================================
# LANDMARK MATCHER CLASS
# =============================================================================

class LandmarkMatcher:
    """
    Semantic landmark matcher using sentence embeddings.
    
    Pipeline:
    1. Load landmarks from CSV
    2. Build embeddings for all landmark names
    3. For user queries, compute embedding and find nearest neighbors
    4. Return matches with similarity scores
    
    ML Notes:
    - Uses cosine similarity for matching (normalized dot product)
    - Embeddings capture semantic meaning ("big temple" ≈ "Hanuman Mandir")
    - City filtering is applied before similarity search for efficiency
    - Falls back to fuzzy string matching if transformers unavailable
    """
    
    # Default model - lightweight and fast
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    
    def __init__(
        self,
        data_path: Optional[str] = None,
        model_name: str = None,
        use_embeddings: bool = True,
        similarity_threshold: float = 0.5,
    ):
        """
        Initialize landmark matcher.
        
        Args:
            data_path: Path to landmarks.csv (or directory containing it)
            model_name: Sentence transformer model to use
            use_embeddings: Use embeddings (False = fuzzy matching only)
            similarity_threshold: Minimum similarity for valid match
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings and SENTENCE_TRANSFORMERS_AVAILABLE
        
        # Resolve data path
        if data_path:
            self.data_path = Path(data_path)
        else:
            self.data_path = Path(__file__).parent / "data"
        
        # Load landmarks
        self._landmarks: List[Landmark] = []
        self._landmarks_by_city: Dict[str, List[Landmark]] = {}
        self._load_landmarks()
        
        # Initialize embedding model
        self._model = None
        self._embeddings: Optional[np.ndarray] = None
        self._landmark_names: List[str] = []
        
        if self.use_embeddings and self._landmarks:
            self._init_model(model_name or self.DEFAULT_MODEL)
            self._build_embeddings()
    
    def _load_landmarks(self):
        """
        Load landmarks from CSV file.
        
        Expected schema:
        - name (string): Landmark name
        - type (string): Category
        - latitude (float): Lat coordinate
        - longitude (float): Lon coordinate
        - city (string): City name
        """
        csv_path = self.data_path / "landmarks.csv"
        if self.data_path.suffix == ".csv":
            csv_path = self.data_path
        
        if not csv_path.exists():
            print(f"Warning: landmarks.csv not found at {csv_path}")
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        landmark = Landmark(
                            name=row['name'].strip(),
                            type=row.get('type', 'unknown').strip().lower(),
                            latitude=float(row['latitude']),
                            longitude=float(row['longitude']),
                            city=row['city'].strip().lower(),
                        )
                        self._landmarks.append(landmark)
                        
                        # Index by city
                        if landmark.city not in self._landmarks_by_city:
                            self._landmarks_by_city[landmark.city] = []
                        self._landmarks_by_city[landmark.city].append(landmark)
                        
                    except (KeyError, ValueError) as e:
                        continue  # Skip malformed rows
                        
            print(f"Loaded {len(self._landmarks)} landmarks from {csv_path}")
            
        except Exception as e:
            print(f"Error loading landmarks: {e}")
    
    def _init_model(self, model_name: str):
        """
        Initialize sentence transformer model.
        
        ML Note: We use all-MiniLM-L6-v2 by default because:
        - Small size (22MB) - fast to download and load
        - Good quality for semantic similarity tasks
        - Produces 384-dim embeddings (compact)
        - Optimized for cosine similarity
        """
        try:
            print(f"Loading sentence transformer model: {model_name}")
            self._model = SentenceTransformer(model_name)
            print(f"Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.use_embeddings = False
    
    def _build_embeddings(self):
        """
        Build embeddings for all landmark names.
        
        ML Note: We pre-compute embeddings for all landmarks at init time.
        This is a one-time cost that makes matching O(1) per query
        (just a matrix multiplication instead of re-encoding landmarks).
        """
        if not self._model or not self._landmarks:
            return
        
        # Get all landmark names
        self._landmark_names = [lm.name for lm in self._landmarks]
        
        print(f"Building embeddings for {len(self._landmark_names)} landmarks...")
        
        # Encode all names in batch (more efficient than one-by-one)
        self._embeddings = self._model.encode(
            self._landmark_names,
            convert_to_numpy=True,
            normalize_embeddings=True,  # Normalize for cosine similarity
            show_progress_bar=False,
        )
        
        print(f"Embeddings built: shape {self._embeddings.shape}")
    
    def match_landmark(
        self,
        user_phrase: str,
        city: Optional[str] = None,
        top_k: int = 1,
    ) -> List[Dict]:
        """
        Match a user landmark phrase to POIs in the dataset.
        
        Args:
            user_phrase: Extracted landmark phrase (e.g., "big temple")
            city: City to filter by (optional, improves accuracy)
            top_k: Number of top matches to return
            
        Returns:
            List of match result dictionaries
            
        ML Note: Matching process:
        1. Filter landmarks by city (if provided)
        2. Encode user phrase to embedding
        3. Compute cosine similarity with all candidate embeddings
        4. Return top-k matches above threshold
        """
        if not user_phrase:
            return []
        
        # Get candidate landmarks
        if city:
            candidates = self._landmarks_by_city.get(city.lower(), [])
            if not candidates:
                # Fall back to all landmarks if city not found
                candidates = self._landmarks
        else:
            candidates = self._landmarks
        
        if not candidates:
            return []
        
        # Use embeddings if available, otherwise fuzzy matching
        if self.use_embeddings and self._model:
            return self._match_with_embeddings(user_phrase, candidates, top_k)
        else:
            return self._match_with_fuzzy(user_phrase, candidates, top_k)
    
    def _match_with_embeddings(
        self,
        user_phrase: str,
        candidates: List[Landmark],
        top_k: int,
    ) -> List[Dict]:
        """
        Match using semantic embeddings.
        
        ML Note: Cosine similarity after normalization is just a dot product.
        Higher score = more semantically similar.
        """
        # Encode user phrase
        query_embedding = self._model.encode(
            user_phrase,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        
        # Get embeddings for candidates
        candidate_names = [c.name for c in candidates]
        candidate_indices = [
            i for i, lm in enumerate(self._landmarks) 
            if lm in candidates
        ]
        
        if not candidate_indices:
            return []
        
        # Get subset of pre-computed embeddings
        candidate_embeddings = self._embeddings[candidate_indices]
        
        # Compute cosine similarities (dot product since normalized)
        similarities = np.dot(candidate_embeddings, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            sim = float(similarities[idx])
            if sim >= self.similarity_threshold:
                lm = candidates[idx]
                result = MatchResult(
                    input_landmark=user_phrase,
                    matched_name=lm.name,
                    lat=lm.latitude,
                    lng=lm.longitude,
                    similarity=sim,
                    landmark_type=lm.type,
                    city=lm.city,
                )
                results.append(result.to_dict())
        
        return results
    
    def _match_with_fuzzy(
        self,
        user_phrase: str,
        candidates: List[Landmark],
        top_k: int,
    ) -> List[Dict]:
        """
        Fallback matching using fuzzy string similarity.
        
        Used when sentence-transformers is not available.
        Less accurate than embeddings but still useful.
        """
        if not RAPIDFUZZ_AVAILABLE:
            return []
        
        candidate_names = [c.name for c in candidates]
        
        # Use token_sort_ratio for better handling of word order variations
        matches = process.extract(
            user_phrase,
            candidate_names,
            scorer=fuzz.token_sort_ratio,
            limit=top_k,
        )
        
        results = []
        for name, score, idx in matches:
            # Convert score from 0-100 to 0-1
            similarity = score / 100.0
            
            if similarity >= self.similarity_threshold:
                lm = candidates[idx]
                result = MatchResult(
                    input_landmark=user_phrase,
                    matched_name=lm.name,
                    lat=lm.latitude,
                    lng=lm.longitude,
                    similarity=similarity,
                    landmark_type=lm.type,
                    city=lm.city,
                )
                results.append(result.to_dict())
        
        return results
    
    def get_landmarks_in_city(self, city: str) -> List[Dict]:
        """Get all landmarks in a specific city."""
        landmarks = self._landmarks_by_city.get(city.lower(), [])
        return [lm.to_dict() for lm in landmarks]
    
    def get_all_cities(self) -> List[str]:
        """Get list of all cities with landmarks."""
        return list(self._landmarks_by_city.keys())
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded landmarks."""
        return {
            "total_landmarks": len(self._landmarks),
            "cities": len(self._landmarks_by_city),
            "embeddings_available": self._embeddings is not None,
            "embedding_dim": self._embeddings.shape[1] if self._embeddings is not None else 0,
        }


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# =============================================================================

# Global matcher instance (lazy initialization)
_global_matcher: Optional[LandmarkMatcher] = None


def get_matcher(data_path: Optional[str] = None, **kwargs) -> LandmarkMatcher:
    """
    Get or create the global landmark matcher instance.
    
    Args:
        data_path: Path to landmarks data
        **kwargs: Additional options for LandmarkMatcher
        
    Returns:
        LandmarkMatcher instance
    """
    global _global_matcher
    
    if _global_matcher is None or data_path is not None:
        _global_matcher = LandmarkMatcher(data_path=data_path, **kwargs)
    
    return _global_matcher


def load_landmarks(data_path: Optional[str] = None) -> List[Dict]:
    """
    Load landmarks from CSV and return as list of dicts.
    
    Args:
        data_path: Path to landmarks.csv
        
    Returns:
        List of landmark dictionaries
    """
    matcher = get_matcher(data_path, use_embeddings=False)
    return [lm.to_dict() for lm in matcher._landmarks]


def build_landmark_embeddings(data_path: Optional[str] = None, model_name: str = None):
    """
    Build embeddings for all landmarks.
    
    Call this once at startup to pre-compute embeddings.
    
    Args:
        data_path: Path to landmarks.csv
        model_name: Sentence transformer model name
    """
    global _global_matcher
    
    kwargs = {"use_embeddings": True}
    if model_name:
        kwargs["model_name"] = model_name
    
    _global_matcher = LandmarkMatcher(data_path=data_path, **kwargs)
    
    return _global_matcher.get_stats()


def match_landmark(
    user_phrase: str,
    city: Optional[str] = None,
    top_k: int = 1,
) -> List[Dict]:
    """
    Match a user landmark phrase to POIs in the dataset.
    
    Args:
        user_phrase: Landmark phrase from address (e.g., "big temple")
        city: City to filter by (optional)
        top_k: Number of matches to return
        
    Returns:
        List of match results with similarity scores
        
    Example:
        >>> match_landmark("big temple", city="indore")
        [{"input_landmark": "big temple", "matched_name": "Hanuman Mandir", 
          "lat": 22.7201, "lng": 75.8589, "similarity": 0.87}]
    """
    matcher = get_matcher()
    return matcher.match_landmark(user_phrase, city=city, top_k=top_k)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("Landmark Matcher Demo")
    print("=" * 50)
    
    # Check if we have the required dependencies
    print(f"\nDependencies:")
    print(f"  sentence-transformers: {'✓' if SENTENCE_TRANSFORMERS_AVAILABLE else '✗'}")
    print(f"  rapidfuzz: {'✓' if RAPIDFUZZ_AVAILABLE else '✗'}")
    
    # Try to load landmarks
    print(f"\nLoading landmarks...")
    try:
        stats = build_landmark_embeddings()
        print(f"Stats: {stats}")
        
        # Test matching
        test_phrases = [
            ("big temple", "mumbai"),
            ("railway station", "delhi"),
            ("city hospital", None),
        ]
        
        print(f"\nTest Matches:")
        for phrase, city in test_phrases:
            results = match_landmark(phrase, city=city)
            if results:
                r = results[0]
                print(f"  '{phrase}' ({city or 'any'}) → {r['matched_name']} (sim: {r['similarity']:.2f})")
            else:
                print(f"  '{phrase}' ({city or 'any'}) → No match found")
                
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure landmarks.csv exists in the data directory")
