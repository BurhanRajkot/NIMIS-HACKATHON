"""
Health check route.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with status
    """
    return jsonify({
        'status': 'ok',
        'service': 'Smart Address Intelligence API',
        'version': '1.0.0'
    }), 200
