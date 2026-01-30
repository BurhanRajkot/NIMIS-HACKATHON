#!/usr/bin/env python
"""
Demo script for Geospatial NLP Indian Address Processing.

This script demonstrates the end-to-end pipeline:
1. Address normalization
2. Landmark extraction  
3. Contextual geocoding
4. Confidence scoring

Run: python demo.py
"""

import json
import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

from geospatial_nlp import process_address
from geospatial_nlp.normalizer import normalize_address
from geospatial_nlp.landmark_extractor import extract_landmarks
from geospatial_nlp.geocoder import geocode_address
from geospatial_nlp.data_loader import get_data_loader


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(result: dict, title: str = "Result"):
    """Pretty print a result dictionary."""
    print(f"\n{title}:")
    print(json.dumps(result, indent=2, default=str))


def demo_normalization():
    """Demonstrate address normalization."""
    print_section("1. ADDRESS NORMALIZATION")
    
    test_addresses = [
        "opp to shiv mandir, nr railway stn, andheri (e), mumbai-400069",
        "H.No. 42, Ram Gali, Nr SBI Bank, Jaipur RJ",
        "Flat 203, ABC Bldg, Opp City Mall, MG Rd, Bangalore 560001",
        "Behind Gurudwara Sahib, Sector 21, Chandigarh",
    ]
    
    for addr in test_addresses:
        print(f"\n📍 Input: {addr}")
        result = normalize_address(addr)
        print(f"   Normalized: {result['text']}")
        print(f"   Pincode: {result['pincode']}")
        print(f"   City: {result['city']}")
        print(f"   State: {result['state']}")


def demo_landmark_extraction():
    """Demonstrate landmark extraction."""
    print_section("2. LANDMARK EXTRACTION")
    
    test_addresses = [
        "Near Shiv Temple, Opposite Railway Station, Mumbai",
        "Behind City Hospital, Near Metro Station, Delhi",
        "Adjacent to Crawford Market, Near GPO, Mumbai",
    ]
    
    for addr in test_addresses:
        print(f"\n📍 Input: {addr}")
        landmarks = extract_landmarks(addr)
        print(f"   Found {len(landmarks)} landmarks:")
        for lm in landmarks:
            pos = f" ({lm['position']})" if lm.get('position') else ""
            print(f"   - {lm['normalized']} [{lm['category']}]{pos} (conf: {lm['confidence']:.2f})")


def demo_geocoding():
    """Demonstrate contextual geocoding."""
    print_section("3. CONTEXTUAL GEOCODING")
    
    test_cases = [
        {"address": "Andheri East", "pincode": "400069"},
        {"address": "Connaught Place, Delhi", "pincode": "110001"},
        {"address": "MG Road, Bengaluru", "pincode": "560001"},
        {"address": "Some Unknown Place", "pincode": None},
    ]
    
    for case in test_cases:
        print(f"\n📍 Input: {case['address']} (PIN: {case['pincode']})")
        result = geocode_address(case['address'], pincode=case['pincode'])
        coords = result['coordinates']
        print(f"   Coordinates: ({coords['lat']:.4f}, {coords['lon']:.4f})")
        print(f"   Source: {result['source']}")
        print(f"   Precision: {result['precision']}")
        print(f"   Uncertainty: ±{result['uncertainty_km']:.1f} km")


def demo_full_pipeline():
    """Demonstrate the full processing pipeline."""
    print_section("4. FULL PIPELINE")
    
    test_addresses = [
        "Flat 302, Sunrise Apts, opp to shiv mandir, nr railway stn, andheri (e), mumbai-400069",
        "H.No. 15, Behind Gurudwara Sahib, Near Metro Station, Sector 21, Delhi-110001",
        "Shop 5, Ground Flr, Opp City Hospital, MG Rd, Bangalore",
    ]
    
    for addr in test_addresses:
        print(f"\n📍 Processing: {addr}")
        print("-" * 50)
        
        result = process_address(addr)
        
        print(f"\n   📝 Normalized Address:")
        print(f"      {result['normalized_address']}")
        
        print(f"\n   📍 Location Info:")
        print(f"      Pincode: {result['pincode']}")
        print(f"      City: {result['city']}")
        print(f"      State: {result['state']}")
        
        print(f"\n   🏛️  Landmarks Found: {len(result['landmarks'])}")
        for lm in result['landmarks'][:3]:  # Show first 3
            print(f"      - {lm['normalized']} [{lm['category']}]")
        
        if result['coordinates']:
            lat, lon = result['coordinates']['lat'], result['coordinates']['lon']
            print(f"\n   🌍 Coordinates: ({lat:.4f}, {lon:.4f})")
            print(f"      Source: {result['geo_source']}")
        
        conf = result['confidence']
        print(f"\n   ✅ Confidence: {conf['score']:.2f} ({conf['level']})")
        print(f"      {conf['interpretation']}")


def demo_data_loader():
    """Demonstrate data loader functionality."""
    print_section("5. DATA LOADER")
    
    loader = get_data_loader()
    stats = loader.get_stats()
    
    print("\n📊 Loaded Data Statistics:")
    print(f"   Landmarks: {stats['landmarks_count']}")
    print(f"   Delivery Records: {stats['delivery_records_count']}")
    print(f"   Locality Aliases: {stats['locality_aliases_count']}")
    
    # Demo landmark search
    print("\n🔍 Searching for 'Railway Station' landmark in Mumbai...")
    landmark = loader.find_landmark("Railway Station", city="mumbai")
    if landmark:
        print(f"   Found: {landmark.name} at ({landmark.latitude}, {landmark.longitude})")
    else:
        print("   Not found in dataset (expected if no landmarks.csv loaded)")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("  GEOSPATIAL NLP FOR INDIAN ADDRESSES - DEMO")
    print("="*60)
    print("\nThis demo shows the modular ML pipeline for processing")
    print("messy, informal Indian addresses.")
    
    demo_normalization()
    demo_landmark_extraction()
    demo_geocoding()
    demo_full_pipeline()
    demo_data_loader()
    
    print_section("DEMO COMPLETE")
    print("\nThe pipeline successfully processed addresses through:")
    print("  ✓ Text normalization (abbreviations, transliterations)")
    print("  ✓ Landmark extraction (pattern + positional)")
    print("  ✓ Contextual geocoding (pincode → city → state)")
    print("  ✓ Confidence scoring (component-based)")
    print("\nReady for backend integration!")


if __name__ == "__main__":
    main()
