"""
Smart Address Intelligence API - Flask Application

A production-ready Flask backend for normalizing, geocoding, and analyzing
Indian addresses using rule-based logic and landmark matching.
"""

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    """
    Application factory for creating the Flask app.
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    from config.settings import get_config
    config = get_config()
    app.config.from_object(config)
    
    # Enable CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    from routes import health_bp, analyze_bp, landmarks_bp, feedback_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(landmarks_bp)
    app.register_blueprint(feedback_bp)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad Request', 'message': str(error)}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': 'The requested resource was not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500
    
    # CLI commands
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database tables."""
        from database.db import init_db
        init_db()
        print('Database initialized.')
    
    @app.cli.command('seed-db')
    def seed_db_command():
        """Seed the database with sample data."""
        from database.db import init_db, seed_database
        init_db()
        seed_database()
        print('Database seeded.')
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    # Run the development server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     Smart Address Intelligence API                        ║
    ║     Last-Mile Delivery Address Processing for India       ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Endpoints:                                               ║
    ║    GET  /health              - Health check               ║
    ║    POST /analyze-address     - Analyze an address         ║
    ║    GET  /landmarks           - Get landmarks              ║
    ║    POST /feedback            - Submit feedback            ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
