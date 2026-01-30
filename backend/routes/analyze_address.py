"""
Main address analysis route - the core API endpoint.
"""

import time
from flask import Blueprint, request, jsonify
from database.db import get_db, close_db
from database.models import PredictionLog
from services import (
    AddressParser,
    AddressNormalizer,
    LandmarkService,
    Geocoder,
    ConfidenceService,
    ExplanationService
)
from config.settings import Config

analyze_bp = Blueprint('analyze', __name__)


@analyze_bp.route('/analyze-address', methods=['POST'])
def analyze_address():
    """
    Analyze and standardize an address.
    
    Request body:
        {
            "raw_address": "Near big temple after chai shop, 2nd lane",
            "city": "Indore"
        }
    
    Returns:
        JSON response with standardized address, coordinates, confidence, and explanation
    """
    start_time = time.time()
    
    # Parse request
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Request body is required',
            'status': 'error'
        }), 400
    
    raw_address = data.get('raw_address', '').strip()
    city = data.get('city', Config.DEFAULT_CITY).strip()
    
    if not raw_address:
        return jsonify({
            'error': 'raw_address is required',
            'status': 'error'
        }), 400
    
    session = None
    
    try:
        session = get_db()
        
        # Step 1: Parse address text
        parser = AddressParser()
        parsed = parser.parse(raw_address)
        
        # Step 2: Normalize address
        normalizer = AddressNormalizer(session)
        normalized = normalizer.normalize(parsed, city)
        
        # Step 3: Match landmarks
        landmark_service = LandmarkService(session)
        landmark_matches = landmark_service.find_matching_landmarks(parsed, city)
        
        # Step 4: Geocode
        geocoder = Geocoder(session)
        geocode_result = geocoder.geocode(parsed, landmark_matches, city)
        
        # Step 5: Calculate confidence
        confidence_service = ConfidenceService(session)
        confidence_result = confidence_service.calculate_confidence(
            parsed, landmark_matches, geocode_result, city
        )
        
        # Step 6: Generate explanation
        explanation_service = ExplanationService()
        explanation = explanation_service.generate_explanation(
            parsed, landmark_matches, geocode_result, confidence_result
        )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Step 7: Log prediction
        prediction_log = PredictionLog(
            raw_address=raw_address,
            city=city,
            standardized_address=normalized['standardized_address'],
            latitude=geocode_result.get('latitude'),
            longitude=geocode_result.get('longitude'),
            confidence_score=confidence_result['score'],
            confidence_level=confidence_result['level'],
            landmarks_used=explanation['landmarks_used'],
            direction_interpreted=explanation['direction_interpreted'],
            method=geocode_result.get('method'),
            explanation=explanation,
            processing_time_ms=processing_time_ms
        )
        
        session.add(prediction_log)
        session.commit()
        
        # Build response
        response = {
            'standardized_address': normalized['standardized_address'],
            'coordinates': [
                geocode_result.get('latitude'),
                geocode_result.get('longitude')
            ] if geocode_result.get('latitude') else None,
            'confidence_score': confidence_result['score'],
            'confidence_level': confidence_result['level'],
            'explanation': {
                'landmarks_used': explanation['landmarks_used'],
                'direction_interpreted': explanation['direction_interpreted'],
                'method': explanation['method']
            },
            'prediction_id': prediction_log.id,
            'processing_time_ms': processing_time_ms
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        if session:
            session.rollback()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)


@analyze_bp.route('/analyze-address/<int:prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """
    Get a specific prediction by ID.
    
    Returns:
        JSON response with prediction details
    """
    session = None
    
    try:
        session = get_db()
        
        prediction = session.query(PredictionLog).filter(
            PredictionLog.id == prediction_id
        ).first()
        
        if not prediction:
            return jsonify({
                'error': 'Prediction not found',
                'status': 'error'
            }), 404
        
        return jsonify(prediction.to_dict()), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)
