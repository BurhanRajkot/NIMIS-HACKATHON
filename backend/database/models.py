"""
SQLAlchemy models for Smart Address Intelligence.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON
from database.db import Base


class Landmark(Base):
    """
    Stores known landmarks for address matching.
    """
    __tablename__ = 'landmarks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    landmark_type = Column(String(100))  # temple, mall, shop, monument, etc.
    city = Column(String(100), nullable=False, index=True)
    locality = Column(String(255))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    keywords = Column(Text)  # Comma-separated keywords for fuzzy matching
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'landmark_type': self.landmark_type,
            'city': self.city,
            'locality': self.locality,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'is_active': self.is_active
        }


class LocalityAlias(Base):
    """
    Maps common locality aliases to canonical names.
    """
    __tablename__ = 'locality_aliases'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(255), nullable=False, index=True)
    canonical_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'alias': self.alias,
            'canonical_name': self.canonical_name,
            'city': self.city
        }


class DeliveryHistory(Base):
    """
    Stores historical delivery data for confidence scoring.
    """
    __tablename__ = 'delivery_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_address = Column(Text, nullable=False)
    standardized_address = Column(Text)
    city = Column(String(100), nullable=False, index=True)
    locality = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    delivery_success = Column(Boolean, default=True)
    delivery_time_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'raw_address': self.raw_address,
            'standardized_address': self.standardized_address,
            'city': self.city,
            'locality': self.locality,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'delivery_success': self.delivery_success,
            'delivery_time_minutes': self.delivery_time_minutes
        }


class PredictionLog(Base):
    """
    Logs all address analysis predictions for auditing and improvement.
    """
    __tablename__ = 'prediction_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    standardized_address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    confidence_score = Column(Float)
    confidence_level = Column(String(20))
    landmarks_used = Column(JSON)  # List of landmark names
    direction_interpreted = Column(String(50))
    method = Column(String(255))
    explanation = Column(JSON)
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'raw_address': self.raw_address,
            'city': self.city,
            'standardized_address': self.standardized_address,
            'coordinates': [self.latitude, self.longitude] if self.latitude and self.longitude else None,
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level,
            'landmarks_used': self.landmarks_used,
            'direction_interpreted': self.direction_interpreted,
            'method': self.method,
            'explanation': self.explanation,
            'processing_time_ms': self.processing_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserFeedback(Base):
    """
    Stores user feedback for correcting predictions.
    """
    __tablename__ = 'user_feedback'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_log_id = Column(Integer)  # Reference to PredictionLog
    raw_address = Column(Text, nullable=False)
    city = Column(String(100))
    predicted_latitude = Column(Float)
    predicted_longitude = Column(Float)
    corrected_latitude = Column(Float)
    corrected_longitude = Column(Float)
    corrected_address = Column(Text)
    feedback_type = Column(String(50))  # correct, incorrect, partial
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prediction_log_id': self.prediction_log_id,
            'raw_address': self.raw_address,
            'city': self.city,
            'predicted_coordinates': [self.predicted_latitude, self.predicted_longitude],
            'corrected_coordinates': [self.corrected_latitude, self.corrected_longitude],
            'corrected_address': self.corrected_address,
            'feedback_type': self.feedback_type,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
