"""
Landmarks route - retrieve and search landmarks.
"""

from flask import Blueprint, request, jsonify
from database.db import get_db, close_db
from services import LandmarkService
from config.settings import Config

landmarks_bp = Blueprint('landmarks', __name__)


@landmarks_bp.route('/landmarks', methods=['GET'])
def get_landmarks():
    """
    Get all landmarks for a city.
    
    Query parameters:
        city: City name (default: Indore)
        search: Optional search query
    
    Returns:
        JSON response with list of landmarks
    """
    city = request.args.get('city', Config.DEFAULT_CITY)
    search = request.args.get('search', '').strip()
    
    session = None
    
    try:
        session = get_db()
        landmark_service = LandmarkService(session)
        
        if search:
            landmarks = landmark_service.search_landmarks(search, city)
        else:
            landmarks = landmark_service.get_landmarks_by_city(city)
        
        return jsonify({
            'city': city,
            'count': len(landmarks),
            'landmarks': landmarks
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)


@landmarks_bp.route('/landmarks/<int:landmark_id>', methods=['GET'])
def get_landmark(landmark_id):
    """
    Get a specific landmark by ID.
    
    Returns:
        JSON response with landmark details
    """
    session = None
    
    try:
        session = get_db()
        landmark_service = LandmarkService(session)
        
        landmark = landmark_service.get_landmark_by_id(landmark_id)
        
        if not landmark:
            return jsonify({
                'error': 'Landmark not found',
                'status': 'error'
            }), 404
        
        return jsonify(landmark), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)


@landmarks_bp.route('/landmarks/types', methods=['GET'])
def get_landmark_types():
    """
    Get all unique landmark types.
    
    Returns:
        JSON response with list of landmark types
    """
    from database.models import Landmark
    
    session = None
    
    try:
        session = get_db()
        
        types = session.query(Landmark.landmark_type).distinct().all()
        type_list = [t[0] for t in types if t[0]]
        
        return jsonify({
            'types': sorted(type_list)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)
