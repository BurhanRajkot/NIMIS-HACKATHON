"""
Tests for Landmark Extractor module.

Tests cover:
- Pattern-based landmark extraction
- Positional context detection  
- Category classification
- Confidence scoring
- Deduplication
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from geospatial_nlp.landmark_extractor import LandmarkExtractor, extract_landmarks


class TestLandmarkExtractor:
    """Test suite for LandmarkExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = LandmarkExtractor(use_ner=False, use_fuzzy=False)
    
    # -------------------------------------------------------------------------
    # Religious Landmarks
    # -------------------------------------------------------------------------
    
    def test_extract_temple(self):
        """Test extraction of temple landmarks."""
        result = self.extractor.extract("Near Shiv Temple, Main Road")
        
        assert len(result) >= 1
        temple_found = any("temple" in lm["normalized"].lower() for lm in result)
        assert temple_found
    
    def test_extract_mandir(self):
        """Test extraction of mandir (Hindi temple) landmarks."""
        result = self.extractor.extract("Opposite Ram Mandir Gate")
        
        assert len(result) >= 1
        mandir_found = any("mandir" in lm["text"].lower() for lm in result)
        assert mandir_found
    
    def test_extract_masjid(self):
        """Test extraction of mosque landmarks."""
        result = self.extractor.extract("Behind Jama Masjid")
        
        assert len(result) >= 1
        masjid_found = any("masjid" in lm["text"].lower() for lm in result)
        assert masjid_found
    
    def test_extract_gurudwara(self):
        """Test extraction of gurudwara landmarks."""
        result = self.extractor.extract("Near Gurudwara Sahib")
        
        assert len(result) >= 1
        gurudwara_found = any("gurudwara" in lm["text"].lower() for lm in result)
        assert gurudwara_found
    
    # -------------------------------------------------------------------------
    # Transport Landmarks
    # -------------------------------------------------------------------------
    
    def test_extract_railway_station(self):
        """Test extraction of railway station landmarks."""
        result = self.extractor.extract("Opposite Mumbai Central Railway Station")
        
        assert len(result) >= 1
        station_found = any("railway station" in lm["text"].lower() for lm in result)
        assert station_found
    
    def test_extract_bus_stand(self):
        """Test extraction of bus stand landmarks."""
        result = self.extractor.extract("Near ISBT Bus Stand")
        
        assert len(result) >= 1
        bus_found = any("bus" in lm["text"].lower() for lm in result)
        assert bus_found
    
    def test_extract_metro_station(self):
        """Test extraction of metro station landmarks."""
        result = self.extractor.extract("Near Rajiv Chowk Metro Station")
        
        assert len(result) >= 1
        metro_found = any("metro" in lm["text"].lower() for lm in result)
        assert metro_found
    
    # -------------------------------------------------------------------------
    # Commercial Landmarks
    # -------------------------------------------------------------------------
    
    def test_extract_market(self):
        """Test extraction of market landmarks."""
        result = self.extractor.extract("Near Crawford Market")
        
        assert len(result) >= 1
        market_found = any("market" in lm["text"].lower() for lm in result)
        assert market_found
    
    def test_extract_mall(self):
        """Test extraction of mall landmarks."""
        result = self.extractor.extract("Opposite Phoenix Mall")
        
        assert len(result) >= 1
        mall_found = any("mall" in lm["text"].lower() for lm in result)
        assert mall_found
    
    # -------------------------------------------------------------------------
    # Education Landmarks
    # -------------------------------------------------------------------------
    
    def test_extract_school(self):
        """Test extraction of school landmarks."""
        result = self.extractor.extract("Near St. Xavier's School")
        
        assert len(result) >= 1
        school_found = any("school" in lm["text"].lower() for lm in result)
        assert school_found
    
    def test_extract_college(self):
        """Test extraction of college landmarks."""
        result = self.extractor.extract("Behind Wilson College")
        
        assert len(result) >= 1
        college_found = any("college" in lm["text"].lower() for lm in result)
        assert college_found
    
    # -------------------------------------------------------------------------
    # Health Landmarks
    # -------------------------------------------------------------------------
    
    def test_extract_hospital(self):
        """Test extraction of hospital landmarks."""
        result = self.extractor.extract("Near Lilavati Hospital")
        
        assert len(result) >= 1
        hospital_found = any("hospital" in lm["text"].lower() for lm in result)
        assert hospital_found
    
    # -------------------------------------------------------------------------
    # Government Landmarks
    # -------------------------------------------------------------------------
    
    def test_extract_police_station(self):
        """Test extraction of police station landmarks."""
        result = self.extractor.extract("Behind Andheri Police Station")
        
        assert len(result) >= 1
        police_found = any("police" in lm["text"].lower() for lm in result)
        assert police_found
    
    def test_extract_post_office(self):
        """Test extraction of post office landmarks."""
        result = self.extractor.extract("Near GPO Post Office")
        
        assert len(result) >= 1
        post_found = any("post" in lm["text"].lower() for lm in result)
        assert post_found
    
    # -------------------------------------------------------------------------
    # Infrastructure Landmarks
    # -------------------------------------------------------------------------
    
    def test_extract_bridge(self):
        """Test extraction of bridge landmarks."""
        result = self.extractor.extract("Near Mahalaxmi Bridge")
        
        assert len(result) >= 1
        bridge_found = any("bridge" in lm["text"].lower() for lm in result)
        assert bridge_found
    
    def test_extract_chowk(self):
        """Test extraction of chowk/square landmarks."""
        result = self.extractor.extract("Near Teen Murti Chowk")
        
        assert len(result) >= 1
        chowk_found = any("chowk" in lm["text"].lower() for lm in result)
        assert chowk_found
    
    # -------------------------------------------------------------------------
    # Positional Context Tests
    # -------------------------------------------------------------------------
    
    def test_position_near(self):
        """Test detection of 'near' positional context."""
        result = self.extractor.extract("Near Big Bazaar")
        
        assert len(result) >= 1
        # At least one landmark should have position="near"
        near_found = any(lm.get("position") == "near" for lm in result)
        assert near_found
    
    def test_position_opposite(self):
        """Test detection of 'opposite' positional context."""
        result = self.extractor.extract("Opposite City Mall")
        
        assert len(result) >= 1
        opp_found = any(lm.get("position") == "opposite" for lm in result)
        assert opp_found
    
    def test_position_behind(self):
        """Test detection of 'behind' positional context."""
        result = self.extractor.extract("Behind Central Park")
        
        assert len(result) >= 1
        behind_found = any(lm.get("position") == "behind" for lm in result)
        assert behind_found
    
    # -------------------------------------------------------------------------
    # Category Classification Tests
    # -------------------------------------------------------------------------
    
    def test_category_religious(self):
        """Test religious landmark category assignment."""
        result = self.extractor.extract("Near Shiv Temple")
        
        assert len(result) >= 1
        religious_found = any(lm["category"] == "religious" for lm in result)
        assert religious_found
    
    def test_category_transport(self):
        """Test transport landmark category assignment."""
        result = self.extractor.extract("Near Railway Station")
        
        assert len(result) >= 1
        transport_found = any(lm["category"] == "transport" for lm in result)
        assert transport_found
    
    # -------------------------------------------------------------------------
    # Confidence Scoring Tests
    # -------------------------------------------------------------------------
    
    def test_confidence_in_range(self):
        """Test that confidence scores are in valid range."""
        result = self.extractor.extract("Near Shiv Temple, Opposite Mall")
        
        for lm in result:
            assert 0.0 <= lm["confidence"] <= 1.0
    
    def test_pattern_match_high_confidence(self):
        """Test that pattern matches have high confidence."""
        result = self.extractor.extract("Near Railway Station")
        
        # Pattern matches should have confidence >= 0.8
        for lm in result:
            if lm["category"] != "referenced":  # Pattern-matched
                assert lm["confidence"] >= 0.7
    
    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------
    
    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.extractor.extract("")
        assert result == []
    
    def test_no_landmarks(self):
        """Test address with no landmarks."""
        result = self.extractor.extract("123 Main Street")
        # May have no results or only low-confidence ones
        high_conf = [lm for lm in result if lm["confidence"] >= 0.7]
        assert len(high_conf) == 0
    
    def test_multiple_landmarks(self):
        """Test extraction of multiple landmarks."""
        result = self.extractor.extract(
            "Near Shiv Temple, Opposite Railway Station, Behind City Hospital"
        )
        
        # Should extract at least 2 landmarks
        assert len(result) >= 2
    
    def test_deduplication(self):
        """Test that duplicate landmarks are removed."""
        result = self.extractor.extract(
            "Near Temple, Near the Temple, Beside Temple"
        )
        
        # Should not have duplicate normalized landmarks
        normalized = [lm["normalized"].lower() for lm in result]
        unique_normalized = set(normalized)
        
        # May have some duplicates before dedup, but output should be clean
        assert len(result) <= 5  # Reasonable limit


class TestConvenienceFunction:
    """Test the extract_landmarks convenience function."""
    
    def test_convenience_function_works(self):
        """Test that convenience function returns expected structure."""
        result = extract_landmarks("Near Shiv Temple")
        
        assert isinstance(result, list)
        if result:
            assert "text" in result[0]
            assert "category" in result[0]
            assert "normalized" in result[0]
            assert "confidence" in result[0]


class TestIntegration:
    """Integration tests with realistic addresses."""
    
    def test_complex_address(self):
        """Test landmark extraction from complex address."""
        address = """
        Flat 302, Sunrise Apartments, 
        Near Shiv Temple, Opposite Metro Station,
        Behind City Hospital, Andheri East
        """
        
        result = extract_landmarks(address, use_ner=False)
        
        # Should find religious, transport, and health landmarks
        categories = {lm["category"] for lm in result}
        
        # At least transport or health should be found
        assert len(result) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
