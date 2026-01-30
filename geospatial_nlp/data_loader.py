"""
Data Loaders for Geospatial NLP System.

Handles loading and caching of external datasets:
1. Landmarks dataset (landmarks.csv) - Known landmark locations
2. Delivery history (delivery_history.csv) - Historical geocoded addresses
3. Locality aliases (locality_aliases.csv) - Standardized locality names

Design notes:
- Lazy loading: Data loaded on first access
- Caching: Data cached in memory after loading
- Fallback: Works without data files using built-in defaults
- Extensible: Easy to add new data sources
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from functools import lru_cache


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class Landmark:
    """
    Represents a known landmark from the landmarks dataset.
    
    Schema matches landmarks.csv:
    - name (string): Landmark name
    - type (string): Category (temple, hospital, etc.)
    - latitude (float): Latitude coordinate
    - longitude (float): Longitude coordinate
    - city (string): City where landmark is located
    """
    name: str
    type: str
    latitude: float
    longitude: float
    city: str
    
    @property
    def coordinates(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "city": self.city,
        }


@dataclass
class DeliveryRecord:
    """
    Represents a historical delivery from delivery_history.csv.
    
    Schema:
    - raw_address (string): Original address text
    - latitude (float): Geocoded latitude
    - longitude (float): Geocoded longitude
    - delivery_status (string): "success" or "failed"
    - city (string): City of delivery
    """
    raw_address: str
    latitude: float
    longitude: float
    delivery_status: str
    city: str
    
    @property
    def coordinates(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)
    
    @property
    def was_successful(self) -> bool:
        return self.delivery_status.lower() == "success"
    
    def to_dict(self) -> dict:
        return {
            "raw_address": self.raw_address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "delivery_status": self.delivery_status,
            "city": self.city,
        }


@dataclass
class LocalityAlias:
    """
    Represents a locality name variation from locality_aliases.csv.
    
    Schema:
    - variant_name (string): Variant/informal name
    - standardized_name (string): Official/standardized name
    - city (string): City context
    """
    variant_name: str
    standardized_name: str
    city: str
    
    def to_dict(self) -> dict:
        return {
            "variant_name": self.variant_name,
            "standardized_name": self.standardized_name,
            "city": self.city,
        }


# =============================================================================
# DATA LOADER CLASS
# =============================================================================

class DataLoader:
    """
    Centralized data loader for all external datasets.
    
    Provides lazy loading with caching:
    - Data is only loaded when first accessed
    - Loaded data is cached for subsequent calls
    - Gracefully handles missing files
    
    Usage:
        loader = DataLoader(data_dir="path/to/data")
        landmarks = loader.get_landmarks()
        aliases = loader.get_locality_aliases(city="mumbai")
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize data loader.
        
        Args:
            data_dir: Path to directory containing CSV files.
                     If None, looks in ./data relative to this module.
        """
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(__file__).parent / "data"
        
        # Cache for loaded data
        self._landmarks_cache: Optional[List[Landmark]] = None
        self._delivery_cache: Optional[List[DeliveryRecord]] = None
        self._aliases_cache: Optional[List[LocalityAlias]] = None
        
        # Indexes for fast lookup
        self._landmarks_by_city: Dict[str, List[Landmark]] = {}
        self._landmarks_by_type: Dict[str, List[Landmark]] = {}
        self._aliases_by_city: Dict[str, Dict[str, str]] = {}
    
    # -------------------------------------------------------------------------
    # Landmarks Dataset
    # -------------------------------------------------------------------------
    
    def get_landmarks(self, reload: bool = False) -> List[Landmark]:
        """
        Load all landmarks from landmarks.csv.
        
        Args:
            reload: Force reload from file even if cached
            
        Returns:
            List of Landmark objects
        """
        if self._landmarks_cache is None or reload:
            self._load_landmarks()
        return self._landmarks_cache or []
    
    def get_landmarks_by_city(self, city: str) -> List[Landmark]:
        """Get all landmarks in a specific city."""
        if not self._landmarks_by_city:
            self.get_landmarks()  # Ensure loaded
        return self._landmarks_by_city.get(city.lower(), [])
    
    def get_landmarks_by_type(self, landmark_type: str) -> List[Landmark]:
        """Get all landmarks of a specific type."""
        if not self._landmarks_by_type:
            self.get_landmarks()  # Ensure loaded
        return self._landmarks_by_type.get(landmark_type.lower(), [])
    
    def find_landmark(
        self,
        name: str,
        city: Optional[str] = None,
        fuzzy: bool = True
    ) -> Optional[Landmark]:
        """
        Find a landmark by name, optionally within a city.
        
        Args:
            name: Landmark name to search for
            city: Optional city to limit search
            fuzzy: Use fuzzy matching if exact match fails
            
        Returns:
            Matching Landmark or None
        """
        landmarks = self.get_landmarks_by_city(city) if city else self.get_landmarks()
        name_lower = name.lower()
        
        # Exact match first
        for lm in landmarks:
            if lm.name.lower() == name_lower:
                return lm
        
        # Fuzzy match if enabled
        if fuzzy:
            try:
                from rapidfuzz import fuzz, process
                names = [lm.name for lm in landmarks]
                result = process.extractOne(name, names, scorer=fuzz.token_sort_ratio, score_cutoff=75)
                if result:
                    matched_name = result[0]
                    for lm in landmarks:
                        if lm.name == matched_name:
                            return lm
            except ImportError:
                pass  # Fuzzy matching not available
        
        return None
    
    def _load_landmarks(self):
        """Load landmarks from CSV file."""
        self._landmarks_cache = []
        self._landmarks_by_city = {}
        self._landmarks_by_type = {}
        
        csv_path = self.data_dir / "landmarks.csv"
        if not csv_path.exists():
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        landmark = Landmark(
                            name=row['name'].strip(),
                            type=row['type'].strip().lower(),
                            latitude=float(row['latitude']),
                            longitude=float(row['longitude']),
                            city=row['city'].strip().lower(),
                        )
                        self._landmarks_cache.append(landmark)
                        
                        # Index by city
                        if landmark.city not in self._landmarks_by_city:
                            self._landmarks_by_city[landmark.city] = []
                        self._landmarks_by_city[landmark.city].append(landmark)
                        
                        # Index by type
                        if landmark.type not in self._landmarks_by_type:
                            self._landmarks_by_type[landmark.type] = []
                        self._landmarks_by_type[landmark.type].append(landmark)
                        
                    except (KeyError, ValueError) as e:
                        # Skip malformed rows
                        continue
        except Exception as e:
            print(f"Warning: Could not load landmarks.csv: {e}")
    
    # -------------------------------------------------------------------------
    # Delivery History Dataset
    # -------------------------------------------------------------------------
    
    def get_delivery_history(self, reload: bool = False) -> List[DeliveryRecord]:
        """
        Load delivery history from delivery_history.csv.
        
        Args:
            reload: Force reload from file even if cached
            
        Returns:
            List of DeliveryRecord objects
        """
        if self._delivery_cache is None or reload:
            self._load_delivery_history()
        return self._delivery_cache or []
    
    def get_successful_deliveries(self, city: Optional[str] = None) -> List[DeliveryRecord]:
        """Get only successful delivery records, optionally filtered by city."""
        records = self.get_delivery_history()
        filtered = [r for r in records if r.was_successful]
        if city:
            filtered = [r for r in filtered if r.city.lower() == city.lower()]
        return filtered
    
    def find_similar_addresses(
        self,
        address: str,
        city: Optional[str] = None,
        limit: int = 5
    ) -> List[DeliveryRecord]:
        """
        Find historical deliveries with similar addresses.
        
        Useful for learning from past successful deliveries
        to improve geocoding of similar addresses.
        
        Args:
            address: Address text to match
            city: Optional city filter
            limit: Maximum results to return
            
        Returns:
            List of similar DeliveryRecords
        """
        records = self.get_successful_deliveries(city)
        
        try:
            from rapidfuzz import fuzz, process
            
            # Create mapping of address -> record
            addr_to_record = {r.raw_address: r for r in records}
            
            # Find similar addresses
            results = process.extract(
                address,
                list(addr_to_record.keys()),
                scorer=fuzz.token_sort_ratio,
                limit=limit
            )
            
            return [addr_to_record[result[0]] for result in results if result[1] > 50]
            
        except ImportError:
            # Without fuzzy matching, just return empty
            return []
    
    def _load_delivery_history(self):
        """Load delivery history from CSV file."""
        self._delivery_cache = []
        
        csv_path = self.data_dir / "delivery_history.csv"
        if not csv_path.exists():
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        record = DeliveryRecord(
                            raw_address=row['raw_address'].strip(),
                            latitude=float(row['latitude']),
                            longitude=float(row['longitude']),
                            delivery_status=row['delivery_status'].strip().lower(),
                            city=row['city'].strip().lower(),
                        )
                        self._delivery_cache.append(record)
                    except (KeyError, ValueError):
                        continue
        except Exception as e:
            print(f"Warning: Could not load delivery_history.csv: {e}")
    
    # -------------------------------------------------------------------------
    # Locality Aliases Dataset
    # -------------------------------------------------------------------------
    
    def get_locality_aliases(self, reload: bool = False) -> List[LocalityAlias]:
        """
        Load locality aliases from locality_aliases.csv.
        
        Args:
            reload: Force reload from file even if cached
            
        Returns:
            List of LocalityAlias objects
        """
        if self._aliases_cache is None or reload:
            self._load_locality_aliases()
        return self._aliases_cache or []
    
    def standardize_locality(
        self,
        variant: str,
        city: Optional[str] = None
    ) -> Optional[str]:
        """
        Convert a locality variant to its standardized form.
        
        Args:
            variant: Variant/informal locality name
            city: City context (helps disambiguate)
            
        Returns:
            Standardized name or None if not found
        """
        if not self._aliases_by_city:
            self.get_locality_aliases()
        
        variant_lower = variant.lower().strip()
        
        # Try city-specific lookup first
        if city:
            city_aliases = self._aliases_by_city.get(city.lower(), {})
            if variant_lower in city_aliases:
                return city_aliases[variant_lower]
        
        # Try all cities
        for city_aliases in self._aliases_by_city.values():
            if variant_lower in city_aliases:
                return city_aliases[variant_lower]
        
        return None
    
    def get_all_variants(self, standardized: str, city: Optional[str] = None) -> List[str]:
        """
        Get all variant names for a standardized locality name.
        
        Useful for building search patterns that match any variant.
        """
        aliases = self.get_locality_aliases()
        
        variants = []
        standardized_lower = standardized.lower()
        
        for alias in aliases:
            if alias.standardized_name.lower() == standardized_lower:
                if city is None or alias.city.lower() == city.lower():
                    variants.append(alias.variant_name)
        
        return variants
    
    def _load_locality_aliases(self):
        """Load locality aliases from CSV file."""
        self._aliases_cache = []
        self._aliases_by_city = {}
        
        csv_path = self.data_dir / "locality_aliases.csv"
        if not csv_path.exists():
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        alias = LocalityAlias(
                            variant_name=row['variant_name'].strip(),
                            standardized_name=row['standardized_name'].strip(),
                            city=row['city'].strip().lower(),
                        )
                        self._aliases_cache.append(alias)
                        
                        # Index by city for fast lookup
                        if alias.city not in self._aliases_by_city:
                            self._aliases_by_city[alias.city] = {}
                        self._aliases_by_city[alias.city][alias.variant_name.lower()] = alias.standardized_name
                        
                    except (KeyError, ValueError):
                        continue
        except Exception as e:
            print(f"Warning: Could not load locality_aliases.csv: {e}")
    
    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------
    
    def clear_cache(self):
        """Clear all cached data, forcing reload on next access."""
        self._landmarks_cache = None
        self._delivery_cache = None
        self._aliases_cache = None
        self._landmarks_by_city = {}
        self._landmarks_by_type = {}
        self._aliases_by_city = {}
    
    def get_stats(self) -> dict:
        """Get statistics about loaded data."""
        return {
            "landmarks_count": len(self.get_landmarks()),
            "delivery_records_count": len(self.get_delivery_history()),
            "locality_aliases_count": len(self.get_locality_aliases()),
            "cities_with_landmarks": list(self._landmarks_by_city.keys()),
            "landmark_types": list(self._landmarks_by_type.keys()),
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Global data loader instance for convenience
_default_loader: Optional[DataLoader] = None


def get_data_loader(data_dir: Optional[str] = None) -> DataLoader:
    """
    Get the default data loader instance.
    
    Creates a singleton loader on first call.
    """
    global _default_loader
    
    if _default_loader is None or data_dir is not None:
        _default_loader = DataLoader(data_dir)
    
    return _default_loader
