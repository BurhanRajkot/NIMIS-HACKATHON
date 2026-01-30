"""
Tests for Address Normalizer module.

Tests cover:
- Abbreviation expansion
- Hindi transliteration handling
- City name normalization
- Pincode extraction
- State/city identification
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from geospatial_nlp.normalizer import AddressNormalizer, normalize_address


class TestAddressNormalizer:
    """Test suite for AddressNormalizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = AddressNormalizer()
    
    # -------------------------------------------------------------------------
    # Abbreviation Tests
    # -------------------------------------------------------------------------
    
    def test_expand_road_abbreviation(self):
        """Test that 'Rd' is expanded to 'road'."""
        result = self.normalizer.normalize("MG Rd, Bangalore")
        assert "road" in result["text"].lower()
    
    def test_expand_near_abbreviation(self):
        """Test that 'Nr' is expanded to 'near'."""
        result = self.normalizer.normalize("Nr Railway Stn")
        assert "near" in result["text"].lower()
    
    def test_expand_opposite_abbreviation(self):
        """Test that 'Opp' is expanded to 'opposite'."""
        result = self.normalizer.normalize("Opp to SBI Bank")
        assert "opposite" in result["text"].lower()
    
    def test_expand_station_abbreviation(self):
        """Test that 'Stn' is expanded to 'station'."""
        result = self.normalizer.normalize("Andheri Stn")
        assert "station" in result["text"].lower()
    
    def test_expand_building_abbreviation(self):
        """Test that 'Bldg' is expanded to 'building'."""
        result = self.normalizer.normalize("ABC Bldg, Floor 2")
        assert "building" in result["text"].lower()
    
    # -------------------------------------------------------------------------
    # Transliteration Tests
    # -------------------------------------------------------------------------
    
    def test_transliterate_gali(self):
        """Test that 'gali' is translated to 'lane'."""
        result = self.normalizer.normalize("Ram Gali")
        assert "lane" in result["text"].lower()
    
    def test_transliterate_chowk(self):
        """Test that 'chowk' is translated to 'square'."""
        result = self.normalizer.normalize("Teen Murti Chowk")
        assert "square" in result["text"].lower()
    
    def test_transliterate_mandir(self):
        """Test that 'mandir' is translated to 'temple'."""
        result = self.normalizer.normalize("Shiv Mandir Road")
        assert "temple" in result["text"].lower()
    
    def test_transliterate_mohalla(self):
        """Test that 'mohalla' is translated to 'locality'."""
        result = self.normalizer.normalize("Rajput Mohalla")
        assert "locality" in result["text"].lower()
    
    # -------------------------------------------------------------------------
    # City Name Normalization Tests
    # -------------------------------------------------------------------------
    
    def test_normalize_bombay_to_mumbai(self):
        """Test that 'Bombay' is normalized to 'mumbai'."""
        result = self.normalizer.normalize("Bombay Central")
        assert "mumbai" in result["text"].lower()
    
    def test_normalize_madras_to_chennai(self):
        """Test that 'Madras' is normalized to 'chennai'."""
        result = self.normalizer.normalize("Madras High Court")
        assert "chennai" in result["text"].lower()
    
    def test_normalize_calcutta_to_kolkata(self):
        """Test that 'Calcutta' is normalized to 'kolkata'."""
        result = self.normalizer.normalize("Calcutta Port")
        assert "kolkata" in result["text"].lower()
    
    def test_normalize_bangalore_to_bengaluru(self):
        """Test that 'Bangalore' is normalized to 'bengaluru'."""
        result = self.normalizer.normalize("Bangalore East")
        assert "bengaluru" in result["text"].lower()
    
    # -------------------------------------------------------------------------
    # Pincode Extraction Tests
    # -------------------------------------------------------------------------
    
    def test_extract_pincode_plain(self):
        """Test extraction of plain 6-digit pincode."""
        result = self.normalizer.normalize("Mumbai 400001")
        assert result["pincode"] == "400001"
    
    def test_extract_pincode_with_hyphen(self):
        """Test extraction of hyphenated pincode."""
        result = self.normalizer.normalize("Mumbai-400069")
        assert result["pincode"] == "400069"
    
    def test_extract_pincode_with_prefix(self):
        """Test extraction of pincode with 'PIN:' prefix."""
        result = self.normalizer.normalize("Andheri East, PIN: 400069")
        assert result["pincode"] == "400069"
    
    def test_no_pincode(self):
        """Test that None is returned when no pincode present."""
        result = self.normalizer.normalize("Andheri East, Mumbai")
        assert result["pincode"] is None
    
    def test_invalid_pincode_not_extracted(self):
        """Test that invalid pincodes (starting with 0) are not extracted."""
        result = self.normalizer.normalize("Phone: 022456789")
        assert result["pincode"] is None
    
    # -------------------------------------------------------------------------
    # Directional Suffix Tests
    # -------------------------------------------------------------------------
    
    def test_expand_east_suffix(self):
        """Test that (E) is expanded to 'East'."""
        result = self.normalizer.normalize("Andheri (E)")
        assert "east" in result["text"].lower()
    
    def test_expand_west_suffix(self):
        """Test that (W) is expanded to 'West'."""
        result = self.normalizer.normalize("Santa Cruz (W)")
        assert "west" in result["text"].lower()
    
    # -------------------------------------------------------------------------
    # State/City Identification Tests
    # -------------------------------------------------------------------------
    
    def test_identify_state_maharashtra(self):
        """Test state identification for Maharashtra."""
        result = self.normalizer.normalize("Mumbai, Maharashtra")
        assert result["state"] == "MH"
    
    def test_identify_city_mumbai(self):
        """Test city identification for Mumbai."""
        result = self.normalizer.normalize("Andheri East, Mumbai")
        assert result["city"] == "Mumbai"
    
    def test_identify_city_delhi(self):
        """Test city identification for Delhi."""
        result = self.normalizer.normalize("Connaught Place, Delhi")
        assert result["city"] == "Delhi"
    
    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------
    
    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.normalizer.normalize("")
        assert result["text"] == ""
        assert result["pincode"] is None
    
    def test_none_input(self):
        """Test handling of None input."""
        result = self.normalizer.normalize(None)
        assert result["text"] == ""
    
    def test_whitespace_normalization(self):
        """Test that multiple spaces are collapsed."""
        result = self.normalizer.normalize("Mumbai   Central    Station")
        assert "  " not in result["text"]
    
    def test_preserves_original(self):
        """Test that original text is preserved in output."""
        original = "Opp Railway Stn, Mumbai-400001"
        result = self.normalizer.normalize(original)
        assert result["original"] == original


class TestConvenienceFunction:
    """Test the normalize_address convenience function."""
    
    def test_convenience_function_works(self):
        """Test that convenience function returns expected structure."""
        result = normalize_address("MG Rd, Bangalore 560001")
        
        assert "text" in result
        assert "pincode" in result
        assert "state" in result
        assert "city" in result
        assert "original" in result
    
    def test_convenience_function_with_options(self):
        """Test that options are passed through."""
        result = normalize_address(
            "Bombay Central",
            normalize_cities=False
        )
        # City should not be normalized
        assert "bombay" in result["text"].lower()


# Sample messy addresses for integration testing
MESSY_ADDRESS_SAMPLES = [
    {
        "input": "opp to shiv mandir, nr railway stn, andheri (e), mumbai-400069",
        "expected_pincode": "400069",
        "expected_city": "Mumbai",
        "contains": ["opposite", "temple", "near", "station", "east"],
    },
    {
        "input": "H.No. 42, Ram Gali, Nr SBI Bank, Jaipur RJ 302001",
        "expected_pincode": "302001",
        "expected_city": "Jaipur",
        "contains": ["house number", "lane", "near"],
    },
    {
        "input": "Flat 203, ABC Bldg, Opp City Mall, MG Rd, Bangalore",
        "expected_pincode": None,
        "expected_city": "Bengaluru",
        "contains": ["building", "opposite", "road"],
    },
]


class TestIntegration:
    """Integration tests with realistic messy addresses."""
    
    def test_messy_addresses(self):
        """Test normalization of messy Indian addresses."""
        normalizer = AddressNormalizer()
        
        for sample in MESSY_ADDRESS_SAMPLES:
            result = normalizer.normalize(sample["input"])
            
            # Check pincode
            assert result["pincode"] == sample["expected_pincode"], \
                f"Pincode mismatch for: {sample['input']}"
            
            # Check city
            if sample["expected_city"]:
                assert result["city"] == sample["expected_city"], \
                    f"City mismatch for: {sample['input']}"
            
            # Check expected terms are present
            text_lower = result["text"].lower()
            for term in sample["contains"]:
                assert term in text_lower, \
                    f"Expected '{term}' in normalized text for: {sample['input']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
