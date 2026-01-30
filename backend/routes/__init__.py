"""Routes package initialization."""
from .health import health_bp
from .analyze_address import analyze_bp
from .landmarks import landmarks_bp
from .feedback import feedback_bp

__all__ = ['health_bp', 'analyze_bp', 'landmarks_bp', 'feedback_bp']
