"""
Application configuration settings.
Loads environment variables and provides configuration classes.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Application
    DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'Indore')
    
    # Geocoding offsets (in degrees, approximately)
    DIRECTION_OFFSETS = {
        'near': 0.0001,      # ~11 meters
        'behind': 0.0002,    # ~22 meters
        'after': 0.00015,    # ~17 meters
        'before': 0.00015,   # ~17 meters
        'opposite': 0.0002,  # ~22 meters
        'next to': 0.00005,  # ~5.5 meters
        'beside': 0.00005,   # ~5.5 meters
    }
    
    # Confidence thresholds
    CONFIDENCE_HIGH = 0.75
    CONFIDENCE_MEDIUM = 0.50
    CONFIDENCE_LOW = 0.25


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the current configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
