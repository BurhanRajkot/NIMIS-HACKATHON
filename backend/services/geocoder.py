"""
Geocoder service - converts addresses to coordinates using rule-based logic.
"""

from utils.geo_utils import apply_direction_offset, calculate_centroid, format_coordinates
from config.settings import Config


class Geocoder:
    """
    Rule-based geocoder using landmark coordinates and direction offsets.
    """
    
    def __init__(self, db_session=None):
        """
        Initialize the geocoder.
        
        Args:
            db_session: Database session for delivery history lookups
        """
        self.db_session = db_session
        self.config = Config()
    
    def geocode(self, parsed_address, landmark_matches, city):
        """
        Geocode an address using matched landmarks and directional logic.
        
        Args:
            parsed_address: Dictionary from AddressParser
            landmark_matches: List of matched landmarks from LandmarkService
            city: City name
            
        Returns:
            Dictionary with coordinates and method used
        """
        if not landmark_matches:
            # Try to get approximate city center
            city_coords = self._get_city_center(city)
            return {
                'latitude': city_coords[0] if city_coords else None,
                'longitude': city_coords[1] if city_coords else None,
                'method': 'city_center_fallback',
                'accuracy': 'low'
            }
        
        # Get primary landmark
        primary_match = landmark_matches[0]
        primary_landmark = primary_match['landmark']
        
        base_lat = primary_landmark.latitude
        base_lon = primary_landmark.longitude
        
        # Apply direction offset if direction was extracted
        directions = parsed_address.get('directions', [])
        direction = directions[0] if directions else None
        
        if direction:
            offset = self.config.DIRECTION_OFFSETS.get(direction.lower(), 0.0001)
            adjusted_lat, adjusted_lon = apply_direction_offset(
                base_lat, base_lon, direction, offset
            )
        else:
            adjusted_lat, adjusted_lon = base_lat, base_lon
        
        # If multiple landmarks matched, calculate centroid
        if len(landmark_matches) > 1:
            coords = []
            for match in landmark_matches[:3]:  # Use top 3 matches
                lm = match['landmark']
                coords.append((lm.latitude, lm.longitude))
            
            centroid = calculate_centroid(coords)
            if centroid:
                # Weight towards primary landmark
                adjusted_lat = (adjusted_lat * 0.6) + (centroid[0] * 0.4)
                adjusted_lon = (adjusted_lon * 0.6) + (centroid[1] * 0.4)
        
        # Apply delivery history density adjustment
        if self.db_session:
            density_coords = self._get_density_adjusted_coords(
                adjusted_lat, adjusted_lon, city
            )
            if density_coords:
                adjusted_lat, adjusted_lon = density_coords
        
        # Format final coordinates
        final_lat, final_lon = format_coordinates(adjusted_lat, adjusted_lon)
        
        return {
            'latitude': final_lat,
            'longitude': final_lon,
            'method': self._determine_method(direction, len(landmark_matches)),
            'accuracy': self._determine_accuracy(primary_match['match_score'])
        }
    
    def _get_city_center(self, city):
        """
        Get approximate city center coordinates.
        
        Args:
            city: City name
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        # Hardcoded city centers for common Indian cities
        city_centers = {
            'indore': (22.7196, 75.8577),
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.6139, 77.2090),
            'bangalore': (12.9716, 77.5946),
            'bengaluru': (12.9716, 77.5946),
            'chennai': (13.0827, 80.2707),
            'hyderabad': (17.3850, 78.4867),
            'pune': (18.5204, 73.8567),
            'ahmedabad': (23.0225, 72.5714),
            'kolkata': (22.5726, 88.3639),
            'jaipur': (26.9124, 75.7873),
            'lucknow': (26.8467, 80.9462),
            'bhopal': (23.2599, 77.4126),
        }
        
        return city_centers.get(city.lower() if city else '')
    
    def _get_density_adjusted_coords(self, latitude, longitude, city):
        """
        Adjust coordinates based on delivery history density.
        
        Args:
            latitude: Base latitude
            longitude: Base longitude
            city: City name
            
        Returns:
            Adjusted coordinates or None
        """
        from database.models import DeliveryHistory
        
        try:
            # Find successful deliveries near this location
            radius = 0.005  # ~500m
            
            nearby_deliveries = self.db_session.query(DeliveryHistory).filter(
                DeliveryHistory.city.ilike(city),
                DeliveryHistory.delivery_success == True,
                DeliveryHistory.latitude.isnot(None),
                DeliveryHistory.longitude.isnot(None),
                DeliveryHistory.latitude.between(latitude - radius, latitude + radius),
                DeliveryHistory.longitude.between(longitude - radius, longitude + radius)
            ).limit(10).all()
            
            if len(nearby_deliveries) >= 3:
                # Calculate weighted centroid of successful deliveries
                coords = [(d.latitude, d.longitude) for d in nearby_deliveries]
                centroid = calculate_centroid(coords)
                
                if centroid:
                    # Slightly adjust towards delivery density
                    adjusted_lat = (latitude * 0.8) + (centroid[0] * 0.2)
                    adjusted_lon = (longitude * 0.8) + (centroid[1] * 0.2)
                    return (adjusted_lat, adjusted_lon)
            
        except Exception:
            pass
        
        return None
    
    def _determine_method(self, direction, landmark_count):
        """
        Determine the geocoding method description.
        
        Args:
            direction: Direction keyword used
            landmark_count: Number of landmarks matched
            
        Returns:
            Method description string
        """
        parts = []
        
        if landmark_count > 0:
            parts.append("landmark matching")
        
        if direction:
            parts.append(f"directional offset ({direction})")
        
        if landmark_count > 1:
            parts.append("multi-landmark centroid")
        
        parts.append("rule-based")
        
        return " + ".join(parts)
    
    def _determine_accuracy(self, match_score):
        """
        Determine geocoding accuracy level.
        
        Args:
            match_score: Landmark match score
            
        Returns:
            Accuracy level string
        """
        if match_score >= 0.8:
            return 'high'
        elif match_score >= 0.5:
            return 'medium'
        else:
            return 'low'
