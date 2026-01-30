"""
Geographic utility functions.
"""

import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on Earth.
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
        
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth's radius in meters
    
    # Convert to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_phi / 2) ** 2 + 
         math.cos(phi1) * math.cos(phi2) * 
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def apply_direction_offset(latitude, longitude, direction, offset_degrees=0.0002):
    """
    Apply a coordinate offset based on direction keyword.
    
    Args:
        latitude: Base latitude
        longitude: Base longitude
        direction: Direction keyword (near, behind, after, etc.)
        offset_degrees: Offset in degrees (default ~22 meters)
        
    Returns:
        Tuple of (new_latitude, new_longitude)
    """
    direction = direction.lower() if direction else ""
    
    # Direction offsets - approximate based on cardinal directions
    offsets = {
        'near': (0, 0),  # No offset for "near"
        'behind': (-offset_degrees, 0),  # South
        'after': (offset_degrees, 0),  # North
        'before': (-offset_degrees, 0),  # South
        'opposite': (0, offset_degrees),  # East
        'next to': (0, offset_degrees * 0.5),  # Slight east
        'beside': (0, offset_degrees * 0.5),  # Slight east
        'front': (offset_degrees, 0),  # North
        'back': (-offset_degrees, 0),  # South
        'left': (0, -offset_degrees),  # West
        'right': (0, offset_degrees),  # East
    }
    
    lat_offset, lon_offset = offsets.get(direction, (0, 0))
    
    return (latitude + lat_offset, longitude + lon_offset)


def get_bounding_box(latitude, longitude, radius_meters):
    """
    Calculate a bounding box around a point.
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius_meters: Radius of bounding box in meters
        
    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon)
    """
    # Approximate degrees per meter at this latitude
    lat_offset = radius_meters / 111000  # 1 degree lat ≈ 111km
    lon_offset = radius_meters / (111000 * math.cos(math.radians(latitude)))
    
    return (
        latitude - lat_offset,
        latitude + lat_offset,
        longitude - lon_offset,
        longitude + lon_offset
    )


def is_within_radius(lat1, lon1, lat2, lon2, radius_meters):
    """
    Check if two points are within a given radius.
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
        radius_meters: Maximum distance in meters
        
    Returns:
        True if within radius, False otherwise
    """
    distance = calculate_distance(lat1, lon1, lat2, lon2)
    return distance <= radius_meters


def calculate_centroid(coordinates):
    """
    Calculate the centroid of a list of coordinates.
    
    Args:
        coordinates: List of (latitude, longitude) tuples
        
    Returns:
        Tuple of (centroid_lat, centroid_lon) or None if empty
    """
    if not coordinates:
        return None
    
    lat_sum = sum(c[0] for c in coordinates)
    lon_sum = sum(c[1] for c in coordinates)
    count = len(coordinates)
    
    return (lat_sum / count, lon_sum / count)


def format_coordinates(latitude, longitude, precision=6):
    """
    Format coordinates to a specified precision.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        precision: Number of decimal places
        
    Returns:
        Tuple of (formatted_lat, formatted_lon)
    """
    return (round(latitude, precision), round(longitude, precision))


def validate_indian_coordinates(latitude, longitude):
    """
    Validate that coordinates fall within India's bounding box.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        True if within India, False otherwise
    """
    # India's approximate bounding box
    INDIA_MIN_LAT = 6.0
    INDIA_MAX_LAT = 37.0
    INDIA_MIN_LON = 68.0
    INDIA_MAX_LON = 98.0
    
    return (INDIA_MIN_LAT <= latitude <= INDIA_MAX_LAT and
            INDIA_MIN_LON <= longitude <= INDIA_MAX_LON)


def degrees_to_meters(degrees, latitude=22.7):
    """
    Convert degrees to approximate meters at a given latitude.
    
    Args:
        degrees: Distance in degrees
        latitude: Reference latitude (default: Indore's latitude)
        
    Returns:
        Approximate distance in meters
    """
    # At equator: 1 degree ≈ 111,320 meters
    # Adjusted for latitude
    meters_per_degree = 111320 * math.cos(math.radians(latitude))
    return degrees * meters_per_degree


def meters_to_degrees(meters, latitude=22.7):
    """
    Convert meters to approximate degrees at a given latitude.
    
    Args:
        meters: Distance in meters
        latitude: Reference latitude (default: Indore's latitude)
        
    Returns:
        Approximate distance in degrees
    """
    meters_per_degree = 111320 * math.cos(math.radians(latitude))
    return meters / meters_per_degree
