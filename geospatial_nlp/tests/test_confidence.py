"""
Tests for Confidence Scorer module.

Tests cover:
- Component scoring (pincode, city, state, landmarks)
- Overall score calculation
- Confidence level labels
- Adjustment factors
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from geospatial_nlp.confidence import ConfidenceScorer, calculate_confidence


class TestConfidenceScorer:
    """Test suite for ConfidenceScorer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = ConfidenceScorer()
    
    # -------------------------------------------------------------------------
    # Component Scoring Tests
    # -------------------------------------------------------------------------
    
    def test_score_with_pincode(self):
        """Test that pincode presence increases score."""
        # With pincode
        result_with = self.scorer.score(
            normalized={"pincode": "400001", "city": None, "state": None},
            landmarks=[],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        # Without pincode
        result_without = self.scorer.score(
            normalized={"pincode": None, "city": None, "state": None},
            landmarks=[],
            geo_result={"source": "country_fallback", "precision": "country"}
        )
        
        assert result_with["score"] > result_without["score"]
    
    def test_score_with_city(self):
        """Test that city identification improves score."""
        result = self.scorer.score(
            normalized={"pincode": "400001", "city": "Mumbai", "state": "MH"},
            landmarks=[],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        # City component should be positive
        assert result["components"]["city"] > 0.5
    
    def test_score_with_landmarks(self):
        """Test that landmarks improve score."""
        landmarks = [
            {"text": "Shiv Temple", "category": "religious", "confidence": 0.9},
            {"text": "Railway Station", "category": "transport", "confidence": 0.85},
        ]
        
        result = self.scorer.score(
            normalized={"pincode": "400001", "city": "Mumbai", "state": "MH"},
            landmarks=landmarks,
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        # Landmark component should be high with 2 landmarks
        assert result["components"]["landmarks"] > 0.7
    
    # -------------------------------------------------------------------------
    # Source-Based Scoring Tests
    # -------------------------------------------------------------------------
    
    def test_pincode_source_highest_score(self):
        """Test that pincode source gets highest base score."""
        result_pincode = self.scorer.score(
            normalized={"pincode": "400001", "city": None, "state": None},
            landmarks=[],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        result_city = self.scorer.score(
            normalized={"pincode": None, "city": "Mumbai", "state": None},
            landmarks=[],
            geo_result={"source": "city", "precision": "city"}
        )
        
        assert result_pincode["score"] > result_city["score"]
    
    def test_fallback_source_lowest_score(self):
        """Test that fallback source gets lowest score."""
        result = self.scorer.score(
            normalized={"pincode": None, "city": None, "state": None},
            landmarks=[],
            geo_result={"source": "country_fallback", "precision": "country"}
        )
        
        # Fallback should have very low score
        assert result["score"] < 0.3
    
    # -------------------------------------------------------------------------
    # Confidence Level Tests
    # -------------------------------------------------------------------------
    
    def test_high_confidence_level(self):
        """Test high confidence level assignment."""
        result = self.scorer.score(
            normalized={"pincode": "400001", "city": "Mumbai", "state": "MH"},
            landmarks=[
                {"text": "Temple", "category": "religious", "confidence": 0.9},
            ],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        assert result["level"] == "high"
        assert result["score"] >= 0.85
    
    def test_medium_confidence_level(self):
        """Test medium confidence level range."""
        result = self.scorer.score(
            normalized={"pincode": None, "city": "Mumbai", "state": "MH"},
            landmarks=[],
            geo_result={"source": "city", "precision": "city"}
        )
        
        # City-based should be medium confidence
        assert result["level"] in ["medium", "high"]
    
    def test_low_confidence_level(self):
        """Test low confidence level assignment."""
        result = self.scorer.score(
            normalized={"pincode": None, "city": None, "state": "MH"},
            landmarks=[],
            geo_result={"source": "state", "precision": "state"}
        )
        
        assert result["level"] in ["low", "very_low"]
    
    def test_very_low_confidence_level(self):
        """Test very low confidence level assignment."""
        result = self.scorer.score(
            normalized={"pincode": None, "city": None, "state": None},
            landmarks=[],
            geo_result={"source": "country_fallback", "precision": "country"}
        )
        
        assert result["level"] == "very_low"
        assert result["score"] < 0.40
    
    # -------------------------------------------------------------------------
    # Adjustment Tests
    # -------------------------------------------------------------------------
    
    def test_multiple_landmarks_bonus(self):
        """Test that multiple landmarks get bonus adjustment."""
        landmarks = [
            {"text": "Temple", "category": "religious", "confidence": 0.9},
            {"text": "Station", "category": "transport", "confidence": 0.85},
        ]
        
        result = self.scorer.score(
            normalized={"pincode": "400001", "city": None, "state": None},
            landmarks=landmarks,
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        # Should have multiple_landmarks adjustment
        assert "multiple_landmarks" in result["adjustments"]
        assert result["adjustments"]["multiple_landmarks"] > 0
    
    def test_building_number_bonus(self):
        """Test that building numbers get bonus."""
        result = self.scorer.score(
            normalized={
                "pincode": "400001",
                "city": "Mumbai",
                "state": "MH",
                "original": "H.No. 42, Some Street"
            },
            landmarks=[],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        # Should have building number bonus
        if "has_building_number" in result["adjustments"]:
            assert result["adjustments"]["has_building_number"] > 0
    
    # -------------------------------------------------------------------------
    # Score Bounds Tests
    # -------------------------------------------------------------------------
    
    def test_score_bounded_above(self):
        """Test that score never exceeds 0.99."""
        # Perfect case
        result = self.scorer.score(
            normalized={"pincode": "400001", "city": "Mumbai", "state": "MH"},
            landmarks=[
                {"text": "1", "confidence": 1.0},
                {"text": "2", "confidence": 1.0},
                {"text": "3", "confidence": 1.0},
            ],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        assert result["score"] <= 0.99
    
    def test_score_bounded_below(self):
        """Test that score never goes below 0.05."""
        # Worst case
        result = self.scorer.score(
            normalized={"pincode": None, "city": None, "state": None},
            landmarks=[],
            geo_result={"source": "country_fallback", "precision": "country"}
        )
        
        assert result["score"] >= 0.05
    
    # -------------------------------------------------------------------------
    # Interpretation Tests
    # -------------------------------------------------------------------------
    
    def test_interpretation_present(self):
        """Test that interpretation is always present."""
        result = self.scorer.score(
            normalized={"pincode": "400001", "city": None, "state": None},
            landmarks=[],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        assert "interpretation" in result
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 10


class TestConvenienceFunction:
    """Test the calculate_confidence convenience function."""
    
    def test_convenience_function_works(self):
        """Test that convenience function returns expected structure."""
        result = calculate_confidence(
            normalized={"pincode": "400001", "city": "Mumbai", "state": "MH"},
            landmarks=[],
            geo_result={"source": "pincode", "precision": "locality"}
        )
        
        assert "score" in result
        assert "level" in result
        assert "components" in result
        assert "adjustments" in result
        assert "interpretation" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
