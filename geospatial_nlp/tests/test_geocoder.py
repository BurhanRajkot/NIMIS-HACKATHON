"""
Tests for Contextual Geocoder module.

Tests cover:
- Pincode-based geocoding
- City/state fallback
- Coordinate validation
- Uncertainty estimation
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from geospatial_nlp.geocoder import ContextualGeocoder, geocode_address


class TestContextualGeocoder:
    """Test suite for ContextualGeocoder class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.geocoder = ContextualGeocoder(use_external_api=False)
    
    # -------------------------------------------------------------------------
    # Pincode Geocoding Tests
    # -------------------------------------------------------------------------
    
    def test_geocode_by_pincode_mumbai(self):
        """Test geocoding with Mumbai pincode."""
        result = self.geocoder.geocode(
            normalized_text="Andheri East",
            pincode="400069"
        )
        
        assert result["source"] == "pincode"
        assert result["coordinates"]["lat"] is not None
        assert result["coordinates"]["lon"] is not None
        # Should be near Mumbai (lat ~19, lon ~72)
        assert 18.5 < result["coordinates"]["lat"] < 20.0
        assert 72.5 < result["coordinates"]["lon"] < 73.5
    
    def test_geocode_by_pincode_delhi(self):
        """Test geocoding with Delhi pincode."""
        result = self.geocoder.geocode(
            normalized_text="Connaught Place",
            pincode="110001"
        )
        
        assert result["source"] == "pincode"
        # Should be near Delhi (lat ~28, lon ~77)
        assert 28.0 < result["coordinates"]["lat"] < 29.0
        assert 77.0 < result["coordinates"]["lon"] < 78.0
    
    def test_geocode_by_pincode_bengaluru(self):
        """Test geocoding with Bengaluru pincode."""
        result = self.geocoder.geocode(
            normalized_text="MG Road",
            pincode="560001"
        )
        
        assert result["source"] == "pincode"
        # Should be near Bengaluru (lat ~13, lon ~77)
        assert 12.5 < result["coordinates"]["lat"] < 13.5
        assert 77.0 < result["coordinates"]["lon"] < 78.0
    
    def test_geocode_pincode_prefix_fallback(self):
        """Test fallback to pincode prefix when exact pincode not found."""
        # Use a pincode that's not in our sample data but matches prefix
        result = self.geocoder.geocode(
            normalized_text="Some Area",
            pincode="400999"  # 400xxx is Mumbai region
        )
        
        # Should fall back to prefix-based matching
        assert result["source"] in ["pincode_prefix", "city", "country_fallback"]
    
    # -------------------------------------------------------------------------
    # City Fallback Tests
    # -------------------------------------------------------------------------
    
    def test_geocode_by_city_mumbai(self):
        """Test geocoding by city name when no pincode."""
        result = self.geocoder.geocode(
            normalized_text="Andheri East, Mumbai"
        )
        
        # Should fall back to city
        assert result["source"] in ["city", "pincode"]
        assert result["coordinates"]["lat"] is not None
    
    def test_geocode_by_city_delhi(self):
        """Test geocoding by city for Delhi."""
        result = self.geocoder.geocode(
            normalized_text="Saket, Delhi"
        )
        
        assert result["source"] in ["city", "pincode"]
    
    def test_geocode_by_city_chennai(self):
        """Test geocoding by city for Chennai."""
        result = self.geocoder.geocode(
            normalized_text="T Nagar, Chennai"
        )
        
        assert result["source"] in ["city", "pincode"]
    
    # -------------------------------------------------------------------------
    # State Fallback Tests
    # -------------------------------------------------------------------------
    
    def test_geocode_by_state(self):
        """Test geocoding falls back to state when city unknown."""
        result = self.geocoder.geocode(
            normalized_text="Some Village",
            state_hint="MH"
        )
        
        # Should use state centroid
        assert result["source"] in ["state", "country_fallback"]
    
    # -------------------------------------------------------------------------
    # Uncertainty Tests
    # -------------------------------------------------------------------------
    
    def test_pincode_uncertainty(self):
        """Test that pincode geocoding has low uncertainty."""
        result = self.geocoder.geocode(
            normalized_text="Andheri",
            pincode="400069"
        )
        
        # Pincode should have <10km uncertainty
        assert result["uncertainty_km"] <= 10.0
    
    def test_city_uncertainty(self):
        """Test that city geocoding has moderate uncertainty."""
        result = self.geocoder.geocode(
            normalized_text="Mumbai"
        )
        
        # City should have >10km uncertainty
        if result["source"] == "city":
            assert result["uncertainty_km"] >= 10.0
    
    def test_fallback_high_uncertainty(self):
        """Test that fallback has high uncertainty."""
        result = self.geocoder.geocode(
            normalized_text="Unknown Location"
        )
        
        # Country fallback should have very high uncertainty
        if result["source"] == "country_fallback":
            assert result["uncertainty_km"] >= 500.0
    
    # -------------------------------------------------------------------------
    # Precision Tests
    # -------------------------------------------------------------------------
    
    def test_pincode_precision_label(self):
        """Test that pincode results have 'locality' precision."""
        result = self.geocoder.geocode(
            normalized_text="Area",
            pincode="400001"
        )
        
        assert result["precision"] == "locality"
    
    def test_city_precision_label(self):
        """Test that city results have 'city' precision."""
        result = self.geocoder.geocode(
            normalized_text="Some area in Mumbai"
        )
        
        if result["source"] == "city":
            assert result["precision"] == "city"
    
    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------
    
    def test_empty_address(self):
        """Test handling of empty address."""
        result = self.geocoder.geocode(normalized_text="")
        
        # Should return fallback result
        assert result["coordinates"] is not None
        assert result["source"] == "country_fallback"
    
    def test_invalid_pincode(self):
        """Test handling of invalid pincode."""
        result = self.geocoder.geocode(
            normalized_text="Some Address",
            pincode="000000"  # Invalid - starts with 0
        )
        
        # Should not use pincode, fall back to other methods
        assert result["source"] != "pincode"
    
    def test_coordinates_in_india(self):
        """Test that all results are within India bounds."""
        test_cases = [
            {"normalized_text": "Mumbai", "pincode": "400001"},
            {"normalized_text": "Delhi", "pincode": "110001"},
            {"normalized_text": "Chennai"},
            {"normalized_text": "Random Place"},
        ]
        
        for case in test_cases:
            result = self.geocoder.geocode(**case)
            lat = result["coordinates"]["lat"]
            lon = result["coordinates"]["lon"]
            
            # India bounds: lat 6-36, lon 68-98
            assert 6.0 <= lat <= 36.0, f"Lat {lat} out of India bounds"
            assert 68.0 <= lon <= 98.0, f"Lon {lon} out of India bounds"


class TestConvenienceFunction:
    """Test the geocode_address convenience function."""
    
    def test_convenience_function_works(self):
        """Test that convenience function returns expected structure."""
        result = geocode_address("Mumbai", pincode="400001")
        
        assert "coordinates" in result
        assert "source" in result
        assert "precision" in result
        assert "uncertainty_km" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
