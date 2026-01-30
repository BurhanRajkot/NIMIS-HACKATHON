"""
User feedback route - collect corrections for future improvement.
"""

from flask import Blueprint, request, jsonify
from database.db import get_db, close_db
from database.models import UserFeedback, PredictionLog

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit user feedback for a prediction.
    
    Request body:
        {
            "prediction_id": 123,  // Optional
            "raw_address": "Original address text",
            "city": "Indore",
            "predicted_latitude": 22.7215,
            "predicted_longitude": 75.8593,
            "corrected_latitude": 22.7220,
            "corrected_longitude": 75.8600,
            "corrected_address": "Corrected standardized address",  // Optional
            "feedback_type": "incorrect",  // correct, incorrect, partial
            "notes": "Additional comments"  // Optional
        }
    
    Returns:
        JSON response with feedback ID
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Request body is required',
            'status': 'error'
        }), 400
    
    raw_address = data.get('raw_address', '').strip()
    feedback_type = data.get('feedback_type', '').strip()
    
    if not raw_address:
        return jsonify({
            'error': 'raw_address is required',
            'status': 'error'
        }), 400
    
    if feedback_type not in ['correct', 'incorrect', 'partial']:
        return jsonify({
            'error': 'feedback_type must be one of: correct, incorrect, partial',
            'status': 'error'
        }), 400
    
    session = None
    
    try:
        session = get_db()
        
        # Create feedback record
        feedback = UserFeedback(
            prediction_log_id=data.get('prediction_id'),
            raw_address=raw_address,
            city=data.get('city'),
            predicted_latitude=data.get('predicted_latitude'),
            predicted_longitude=data.get('predicted_longitude'),
            corrected_latitude=data.get('corrected_latitude'),
            corrected_longitude=data.get('corrected_longitude'),
            corrected_address=data.get('corrected_address'),
            feedback_type=feedback_type,
            notes=data.get('notes')
        )
        
        session.add(feedback)
        session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback.id
        }), 201
        
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


@feedback_bp.route('/feedback', methods=['GET'])
def get_feedback():
    """
    Get all feedback entries.
    
    Query parameters:
        city: Filter by city
        type: Filter by feedback type
        limit: Maximum number of results (default: 50)
    
    Returns:
        JSON response with list of feedback entries
    """
    city = request.args.get('city')
    feedback_type = request.args.get('type')
    limit = request.args.get('limit', 50, type=int)
    
    session = None
    
    try:
        session = get_db()
        
        query = session.query(UserFeedback)
        
        if city:
            query = query.filter(UserFeedback.city.ilike(city))
        
        if feedback_type:
            query = query.filter(UserFeedback.feedback_type == feedback_type)
        
        feedback_list = query.order_by(
            UserFeedback.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'count': len(feedback_list),
            'feedback': [f.to_dict() for f in feedback_list]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)


@feedback_bp.route('/feedback/<int:feedback_id>', methods=['GET'])
def get_feedback_by_id(feedback_id):
    """
    Get a specific feedback entry by ID.
    
    Returns:
        JSON response with feedback details
    """
    session = None
    
    try:
        session = get_db()
        
        feedback = session.query(UserFeedback).filter(
            UserFeedback.id == feedback_id
        ).first()
        
        if not feedback:
            return jsonify({
                'error': 'Feedback not found',
                'status': 'error'
            }), 404
        
        return jsonify(feedback.to_dict()), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)


@feedback_bp.route('/feedback/correction', methods=['POST'])
def submit_correction():
    """
    Submit a map marker correction (simplified format for frontend).
    
    Request body:
        {
            "original_lat": 22.72032,
            "original_lng": 75.85812,
            "corrected_lat": 22.7211,
            "corrected_lng": 75.8590,
            "prediction_id": 123  // Optional
        }
    
    Returns:
        JSON response with feedback ID
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'error': 'Request body is required',
            'status': 'error'
        }), 400
    
    # Validate required fields
    required_fields = ['original_lat', 'original_lng', 'corrected_lat', 'corrected_lng']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': f'{field} is required',
                'status': 'error'
            }), 400
    
    session = None
    
    try:
        session = get_db()
        
        # Look up the prediction if ID provided
        raw_address = "Map marker correction"
        city = None
        
        if data.get('prediction_id'):
            from database.models import PredictionLog
            prediction = session.query(PredictionLog).filter(
                PredictionLog.id == data.get('prediction_id')
            ).first()
            if prediction:
                raw_address = prediction.raw_address or raw_address
                city = prediction.city
        
        # Create feedback record
        feedback = UserFeedback(
            prediction_log_id=data.get('prediction_id'),
            raw_address=raw_address,
            city=city,
            predicted_latitude=data.get('original_lat'),
            predicted_longitude=data.get('original_lng'),
            corrected_latitude=data.get('corrected_lat'),
            corrected_longitude=data.get('corrected_lng'),
            feedback_type='incorrect',
            notes='Corrected via map marker drag'
        )
        
        session.add(feedback)
        session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Correction submitted successfully',
            'feedback_id': feedback.id
        }), 201
        
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


@feedback_bp.route('/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """
    Get feedback statistics.
    
    Returns:
        JSON response with feedback statistics
    """
    from sqlalchemy import func
    
    session = None
    
    try:
        session = get_db()
        
        # Get counts by type
        type_counts = session.query(
            UserFeedback.feedback_type,
            func.count(UserFeedback.id)
        ).group_by(UserFeedback.feedback_type).all()
        
        stats = {
            'total': sum(c[1] for c in type_counts),
            'by_type': {t[0]: t[1] for t in type_counts if t[0]}
        }
        
        # Calculate accuracy if we have data
        correct_count = stats['by_type'].get('correct', 0)
        total = stats['total']
        
        if total > 0:
            stats['accuracy_rate'] = round(correct_count / total, 2)
        else:
            stats['accuracy_rate'] = None
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
        
    finally:
        if session:
            close_db(session)
