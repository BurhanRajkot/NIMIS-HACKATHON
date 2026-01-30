"""
Map Data Route - Accept ML output and return map-ready data.

This endpoint receives ML-refined address predictions and returns
formatted data for the Google Maps frontend to render.
"""

from flask import Blueprint, request, jsonify
from database.db import get_db, close_db
from database.models import PredictionLog

map_data_bp = Blueprint('map_data', __name__)


@map_data_bp.route('/map-data', methods=['POST'])
def process_map_data():
    """
    Accept ML output JSON and return map-ready response.
    
    Request body (from ML model):
        {
            "raw_address": "Near Hanuman Mandir, 2nd gali, behind railway station",
            "city": "indore",
            "standardized_address": "near hanuman mandir, 2nd lane behind railway station",
            "matched_landmarks": [
                {
                    "matched_name": "Hanuman Mandir",
                    "lat": 22.7201,
                    "lng": 75.8589
                }
            ],
            "predicted_coordinates": {
                "lat": 22.72032,
                "lng": 75.85812
            },
            "confidence": {
                "score": 0.82,
                "level": "HIGH"
            }
        }
    
    Returns:
        {
            "lat": 22.72032,
            "lng": 75.85812,
            "confidence": "HIGH",
            "confidence_score": 0.82,
            "standardized_address": "...",
            "anchor_landmark": "Hanuman Mandir",
            "prediction_id": 123,
            "raw_address": "..."
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Request body is required',
            'status': 'error'
        }), 400
    
    # Validate required fields
    predicted_coords = data.get('predicted_coordinates', {})
    if not predicted_coords.get('lat') or not predicted_coords.get('lng'):
        return jsonify({
            'error': 'predicted_coordinates with lat and lng are required',
            'status': 'error'
        }), 400
    
    # Extract data from ML output
    raw_address = data.get('raw_address', '')
    city = data.get('city', '')
    standardized_address = data.get('standardized_address', raw_address)
    matched_landmarks = data.get('matched_landmarks', [])
    confidence = data.get('confidence', {})
    
    # Get anchor landmark (first matched landmark)
    anchor_landmark = None
    if matched_landmarks and len(matched_landmarks) > 0:
        anchor_landmark = matched_landmarks[0].get('matched_name')
    
    # Store in database
    session = None
    prediction_id = None
    
    try:
        session = get_db()
        
        # Create prediction log entry
        prediction = PredictionLog(
            raw_address=raw_address,
            city=city,
            standardized_address=standardized_address,
            latitude=predicted_coords.get('lat'),
            longitude=predicted_coords.get('lng'),
            confidence_score=confidence.get('score'),
            confidence_level=confidence.get('level'),
            landmarks_used=[lm.get('matched_name') for lm in matched_landmarks],
            method='ml_prediction',
            explanation={
                'anchor_landmark': anchor_landmark,
                'matched_landmarks_count': len(matched_landmarks)
            }
        )
        
        session.add(prediction)
        session.commit()
        prediction_id = prediction.id
        
    except Exception as e:
        if session:
            session.rollback()
        # Continue without storing - return data anyway
        print(f"Warning: Could not store prediction: {e}")
        
    finally:
        if session:
            close_db(session)
    
    # Return map-ready response
    return jsonify({
        'lat': predicted_coords.get('lat'),
        'lng': predicted_coords.get('lng'),
        'confidence': confidence.get('level', 'MEDIUM'),
        'confidence_score': confidence.get('score', 0.5),
        'standardized_address': standardized_address,
        'anchor_landmark': anchor_landmark,
        'prediction_id': prediction_id,
        'raw_address': raw_address,
        'city': city,
        'status': 'success'
    }), 200


@map_data_bp.route('/map-data/demo', methods=['GET'])
def get_demo_data():
    """
    Return demo data for testing the frontend without ML model.
    
    Returns sample map data for Indore, India.
    """
    return jsonify({
        'lat': 22.72032,
        'lng': 75.85812,
        'confidence': 'HIGH',
        'confidence_score': 0.82,
        'standardized_address': 'Near Hanuman Mandir, 2nd Lane, Behind Railway Station, Indore',
        'anchor_landmark': 'Hanuman Mandir',
        'prediction_id': None,
        'raw_address': 'Near Hanuman Mandir, 2nd gali, behind railway station',
        'city': 'Indore',
        'status': 'success'
    }), 200
