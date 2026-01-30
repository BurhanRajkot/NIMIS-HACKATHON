"""
Confidence Scorer Module for Delivery Location Prediction.

Computes a unified confidence score (0-1) based on multiple factors:
- NLP extraction confidence
- Landmark similarity scores
- Geographic features (distance, density)
- Delivery density in area

Approach: Weighted scoring formula (MVP)
- Simple, interpretable weights
- Can be replaced with Logistic Regression or learned model
- Returns both numeric score and categorical level

ML Notes:
- Weights are hand-tuned for MVP
- Can train LogisticRegression on delivery success data
- Feature vector is well-defined for easy model replacement
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


# =============================================================================
# CONSTANTS
# =============================================================================

# Feature weights for weighted scoring
# These sum to ~1.0 for interpretability
FEATURE_WEIGHTS = {
    "nlp_confidence": 0.20,      # How well NLP extraction worked
    "landmark_similarity": 0.30,  # How well landmarks matched
    "geo_distance": 0.25,         # Distance from predicted to anchor
    "density_score": 0.15,        # Delivery density in area
    "component_count": 0.10,      # Number of address components extracted
}

# Confidence level thresholds
CONFIDENCE_LEVELS = {
    "HIGH": 0.80,
    "MEDIUM": 0.60,
    "LOW": 0.40,
    "VERY_LOW": 0.0,
}

# Distance penalty curve parameters
# Beyond this distance, confidence drops significantly
MAX_REASONABLE_DISTANCE_M = 500


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ConfidenceResult:
    """
    Result of confidence scoring.
    
    Contains overall score, level, and component breakdown.
    """
    confidence_score: float
    confidence_level: str
    component_scores: Dict[str, float]
    interpretation: str
    
    def to_dict(self) -> Dict:
        return {
            "confidence_score": round(self.confidence_score, 3),
            "confidence_level": self.confidence_level,
            "component_scores": {
                k: round(v, 3) for k, v in self.component_scores.items()
            },
            "interpretation": self.interpretation,
        }


# =============================================================================
# SCORING FUNCTIONS
# =============================================================================

def normalize_score(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Normalize a value to 0-1 range."""
    if max_val <= min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def distance_to_confidence(distance_m: float) -> float:
    """
    Convert distance in meters to confidence score.
    
    Uses exponential decay:
    - 0m → 1.0 (perfect)
    - 100m → ~0.82
    - 300m → ~0.55
    - 500m → ~0.37
    - 1000m → ~0.14
    
    ML Note: This decay curve is hand-tuned.
    Could be learned from delivery success rates.
    """
    if distance_m <= 0:
        return 1.0
    
    # Exponential decay with λ = distance / 500
    decay_rate = distance_m / MAX_REASONABLE_DISTANCE_M
    return math.exp(-decay_rate)


def aggregate_landmark_scores(landmark_scores: List[float]) -> float:
    """
    Aggregate multiple landmark similarity scores.
    
    Strategy: Weighted average favoring higher scores
    - Best match contributes 60%
    - Average of others contributes 40%
    
    ML Note: This prioritizes confidence when at least one
    landmark matched well, even if others didn't.
    """
    if not landmark_scores:
        return 0.0
    
    if len(landmark_scores) == 1:
        return landmark_scores[0]
    
    sorted_scores = sorted(landmark_scores, reverse=True)
    best_score = sorted_scores[0]
    other_avg = sum(sorted_scores[1:]) / len(sorted_scores[1:])
    
    return 0.6 * best_score + 0.4 * other_avg


def count_components(geo_features: Dict) -> int:
    """Count number of extracted address components."""
    count = 0
    
    # Count directions
    if geo_features.get("directions"):
        count += len(geo_features["directions"])
    
    # Count landmarks
    if geo_features.get("landmarks"):
        count += len(geo_features["landmarks"])
    
    # Count street info
    street_info = geo_features.get("street_info", {})
    if street_info.get("street_numbers"):
        count += len(street_info["street_numbers"])
    if street_info.get("building_numbers"):
        count += len(street_info["building_numbers"])
    
    return count


def component_count_to_score(count: int) -> float:
    """
    Convert component count to confidence score.
    
    More components = higher confidence (up to a point)
    - 0 components → 0.0
    - 1-2 components → 0.3-0.6
    - 3-4 components → 0.7-0.85
    - 5+ components → 0.9-1.0
    """
    if count == 0:
        return 0.0
    elif count <= 2:
        return 0.3 + (count * 0.15)
    elif count <= 4:
        return 0.55 + ((count - 2) * 0.15)
    else:
        return min(1.0, 0.85 + ((count - 4) * 0.05))


def get_confidence_level(score: float) -> str:
    """Map numeric score to categorical level."""
    if score >= CONFIDENCE_LEVELS["HIGH"]:
        return "HIGH"
    elif score >= CONFIDENCE_LEVELS["MEDIUM"]:
        return "MEDIUM"
    elif score >= CONFIDENCE_LEVELS["LOW"]:
        return "LOW"
    else:
        return "VERY_LOW"


def get_interpretation(level: str, component_scores: Dict) -> str:
    """Generate human-readable interpretation of confidence."""
    interpretations = {
        "HIGH": "High confidence - reliable for direct delivery routing",
        "MEDIUM": "Medium confidence - may require driver verification",
        "LOW": "Low confidence - recommend manual review or customer callback",
        "VERY_LOW": "Very low confidence - insufficient data for reliable prediction",
    }
    
    base = interpretations.get(level, "Unknown confidence level")
    
    # Add specific insights based on component scores
    weak_components = [k for k, v in component_scores.items() if v < 0.4]
    if weak_components:
        if "landmark_similarity" in weak_components:
            base += ". Landmark matching was weak."
        if "nlp_confidence" in weak_components:
            base += ". Address parsing had issues."
        if "geo_distance" in weak_components:
            base += ". Predicted location far from anchor."
    
    return base


# =============================================================================
# MAIN SCORING CLASS
# =============================================================================

class ConfidenceScorer:
    """
    Computes unified confidence score for location predictions.
    
    Uses weighted combination of multiple factors.
    Can be extended with LogisticRegression for learned scoring.
    
    ML Notes:
    - score() method returns consistent output format
    - train() method (TODO) would fit LogisticRegression on labeled data
    - Feature extraction is separated for easy model integration
    """
    
    def __init__(
        self,
        weights: Dict[str, float] = None,
        use_model: bool = False,
    ):
        """
        Initialize confidence scorer.
        
        Args:
            weights: Custom feature weights (optional)
            use_model: Use trained ML model instead of weights (TODO)
        """
        self.weights = weights or FEATURE_WEIGHTS.copy()
        self.use_model = use_model
        self._model = None  # Placeholder for LogisticRegression
    
    def score(
        self,
        nlp_conf: float = 0.8,
        landmark_scores: List[float] = None,
        geo_features: Dict = None,
        density_score: float = 0.7,
    ) -> Dict:
        """
        Compute confidence score for a prediction.
        
        Args:
            nlp_conf: NLP extraction confidence (0-1)
            landmark_scores: List of landmark similarity scores
            geo_features: Dict with extracted address components
                Expected: {"directions": [...], "landmarks": [...], "street_info": {...}}
                Can also include: {"distance_m": float} for distance to anchor
            density_score: Delivery density in area (0-1, simulated)
            
        Returns:
            ConfidenceResult as dictionary
            
        Example:
            >>> scorer = ConfidenceScorer()
            >>> result = scorer.score(
            ...     nlp_conf=0.85,
            ...     landmark_scores=[0.87, 0.72],
            ...     geo_features={"directions": ["near"], "distance_m": 100},
            ...     density_score=0.75
            ... )
            >>> print(result["confidence_score"])  # 0.82
        """
        # Default values
        landmark_scores = landmark_scores or []
        geo_features = geo_features or {}
        
        # Calculate component scores
        component_scores = self._calculate_components(
            nlp_conf=nlp_conf,
            landmark_scores=landmark_scores,
            geo_features=geo_features,
            density_score=density_score,
        )
        
        # Calculate weighted sum
        if self.use_model and self._model is not None:
            # ML model path (TODO)
            final_score = self._predict_with_model(component_scores)
        else:
            # Weighted sum path
            final_score = self._weighted_sum(component_scores)
        
        # Ensure bounds
        final_score = max(0.0, min(1.0, final_score))
        
        # Get level and interpretation
        level = get_confidence_level(final_score)
        interpretation = get_interpretation(level, component_scores)
        
        return ConfidenceResult(
            confidence_score=final_score,
            confidence_level=level,
            component_scores=component_scores,
            interpretation=interpretation,
        ).to_dict()
    
    def _calculate_components(
        self,
        nlp_conf: float,
        landmark_scores: List[float],
        geo_features: Dict,
        density_score: float,
    ) -> Dict[str, float]:
        """Calculate individual component scores."""
        components = {}
        
        # NLP confidence (already 0-1)
        components["nlp_confidence"] = max(0.0, min(1.0, nlp_conf))
        
        # Landmark similarity (aggregate)
        components["landmark_similarity"] = aggregate_landmark_scores(landmark_scores)
        
        # Geographic distance score
        distance_m = geo_features.get("distance_m", 100)  # Default 100m
        components["geo_distance"] = distance_to_confidence(distance_m)
        
        # Delivery density (already 0-1)
        components["density_score"] = max(0.0, min(1.0, density_score))
        
        # Component count score
        component_count = count_components(geo_features)
        components["component_count"] = component_count_to_score(component_count)
        
        return components
    
    def _weighted_sum(self, component_scores: Dict[str, float]) -> float:
        """Calculate weighted sum of component scores."""
        total = 0.0
        weight_sum = 0.0
        
        for key, weight in self.weights.items():
            if key in component_scores:
                total += component_scores[key] * weight
                weight_sum += weight
        
        # Normalize by actual weight sum (in case not all components present)
        if weight_sum > 0:
            return total / weight_sum * sum(self.weights.values())
        
        return 0.5  # Default neutral confidence
    
    def _predict_with_model(self, component_scores: Dict[str, float]) -> float:
        """
        Use trained ML model for prediction.
        
        TODO: Implement when training data available.
        Would use sklearn LogisticRegression.
        """
        # Placeholder - falls back to weighted sum
        return self._weighted_sum(component_scores)
    
    def train(self, features: List[Dict], labels: List[int]):
        """
        Train LogisticRegression on labeled data.
        
        TODO: Implement when training data available.
        
        Args:
            features: List of feature dicts (same as component_scores)
            labels: List of binary labels (1 = successful delivery, 0 = failed)
        """
        # Placeholder for future implementation
        raise NotImplementedError(
            "Training not yet implemented. "
            "Provide labeled delivery data to enable."
        )


# =============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTION
# =============================================================================

# Global scorer instance
_global_scorer: Optional[ConfidenceScorer] = None


def get_scorer(**kwargs) -> ConfidenceScorer:
    """Get or create global scorer instance."""
    global _global_scorer
    
    if _global_scorer is None:
        _global_scorer = ConfidenceScorer(**kwargs)
    
    return _global_scorer


def score_confidence(
    nlp_conf: float = 0.8,
    landmark_scores: List[float] = None,
    geo_features: Dict = None,
    density_score: float = 0.7,
) -> Dict:
    """
    Compute confidence score for a prediction.
    
    Args:
        nlp_conf: NLP extraction confidence (0-1, mock for now)
        landmark_scores: List of landmark similarity scores
        geo_features: Dict with extracted components and optional distance_m
        density_score: Delivery density score (0-1, simulated)
        
    Returns:
        Dict with confidence_score and confidence_level
        
    Example:
        >>> result = score_confidence(
        ...     nlp_conf=0.85,
        ...     landmark_scores=[0.87, 0.72],
        ...     geo_features={"directions": ["near"], "distance_m": 100},
        ...     density_score=0.75
        ... )
        >>> result
        {"confidence_score": 0.82, "confidence_level": "HIGH", ...}
    """
    scorer = get_scorer()
    return scorer.score(
        nlp_conf=nlp_conf,
        landmark_scores=landmark_scores,
        geo_features=geo_features,
        density_score=density_score,
    )


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("Confidence Scorer Demo")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "High confidence",
            "nlp_conf": 0.92,
            "landmark_scores": [0.89, 0.78],
            "geo_features": {
                "directions": ["near"],
                "landmarks": [{"phrase": "near temple"}],
                "street_info": {"street_numbers": [{"number": "2"}]},
                "distance_m": 50,
            },
            "density_score": 0.85,
        },
        {
            "name": "Medium confidence",
            "nlp_conf": 0.75,
            "landmark_scores": [0.65],
            "geo_features": {
                "directions": ["behind"],
                "distance_m": 200,
            },
            "density_score": 0.60,
        },
        {
            "name": "Low confidence",
            "nlp_conf": 0.50,
            "landmark_scores": [0.40],
            "geo_features": {
                "distance_m": 400,
            },
            "density_score": 0.30,
        },
    ]
    
    scorer = ConfidenceScorer()
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        result = scorer.score(
            nlp_conf=case["nlp_conf"],
            landmark_scores=case["landmark_scores"],
            geo_features=case["geo_features"],
            density_score=case["density_score"],
        )
        print(f"  Score: {result['confidence_score']:.3f}")
        print(f"  Level: {result['confidence_level']}")
        print(f"  Components: {result['component_scores']}")
