"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from config.settings import get_config

# Get configuration
config = get_config()

# Update connection string to use psycopg (v3) driver
database_url = config.DATABASE_URL
if database_url and database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

# Create database engine
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=config.SQLALCHEMY_ECHO
)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Base class for models
Base = declarative_base()


def get_db():
    """Get a database session."""
    session = Session()
    try:
        return session
    except Exception:
        session.rollback()
        raise


def close_db(session):
    """Close a database session."""
    if session:
        session.close()


def init_db():
    """Initialize the database by creating all tables."""
    from database.models import (
        Landmark, LocalityAlias, DeliveryHistory, 
        PredictionLog, UserFeedback
    )
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")


def seed_database():
    """Seed the database with sample data."""
    from database.models import Landmark, LocalityAlias
    
    session = get_db()
    
    try:
        # Check if data already exists
        existing_landmarks = session.query(Landmark).first()
        if existing_landmarks:
            print("Database already seeded.")
            return
        
        # Sample landmarks for Indore
        landmarks = [
            Landmark(
                name="Hanuman Mandir",
                landmark_type="temple",
                city="Indore",
                locality="Vijay Nagar",
                latitude=22.7515,
                longitude=75.8930,
                keywords="hanuman,temple,mandir,bajrang"
            ),
            Landmark(
                name="Rajwada Palace",
                landmark_type="monument",
                city="Indore",
                locality="Rajwada",
                latitude=22.7196,
                longitude=75.8577,
                keywords="rajwada,palace,holkar,historical"
            ),
            Landmark(
                name="Sharma Tea Stall",
                landmark_type="shop",
                city="Indore",
                locality="Palasia",
                latitude=22.7230,
                longitude=75.8700,
                keywords="sharma,tea,chai,stall"
            ),
            Landmark(
                name="Central Mall",
                landmark_type="mall",
                city="Indore",
                locality="RNT Marg",
                latitude=22.7180,
                longitude=75.8550,
                keywords="central,mall,shopping"
            ),
            Landmark(
                name="Treasure Island Mall",
                landmark_type="mall",
                city="Indore",
                locality="MG Road",
                latitude=22.7220,
                longitude=75.8780,
                keywords="treasure,island,mall,ti"
            ),
            Landmark(
                name="Lalbagh Palace",
                landmark_type="monument",
                city="Indore",
                locality="Lalbagh",
                latitude=22.7127,
                longitude=75.8486,
                keywords="lalbagh,palace,holkar,museum"
            ),
            Landmark(
                name="Sarafa Bazaar",
                landmark_type="market",
                city="Indore",
                locality="Sarafa",
                latitude=22.7172,
                longitude=75.8573,
                keywords="sarafa,bazaar,market,food,street"
            ),
            Landmark(
                name="Khajrana Ganesh Temple",
                landmark_type="temple",
                city="Indore",
                locality="Khajrana",
                latitude=22.7340,
                longitude=75.9090,
                keywords="khajrana,ganesh,temple,mandir"
            ),
            Landmark(
                name="Apollo DB Mall",
                landmark_type="mall",
                city="Indore",
                locality="Vijay Nagar",
                latitude=22.7530,
                longitude=75.8890,
                keywords="apollo,db,mall,vijay nagar"
            ),
            Landmark(
                name="Annapurna Temple",
                landmark_type="temple",
                city="Indore",
                locality="Sudama Nagar",
                latitude=22.6980,
                longitude=75.8700,
                keywords="annapurna,temple,mandir"
            ),
            Landmark(
                name="Gandhi Hall",
                landmark_type="landmark",
                city="Indore",
                locality="MG Road",
                latitude=22.7200,
                longitude=75.8620,
                keywords="gandhi,hall,town hall,clock tower"
            ),
            Landmark(
                name="Geeta Bhawan",
                landmark_type="religious",
                city="Indore",
                locality="Bhanwarkuan",
                latitude=22.7410,
                longitude=75.8670,
                keywords="geeta,bhawan,gita,religious"
            ),
        ]
        
        # Sample locality aliases
        aliases = [
            LocalityAlias(alias="VN", canonical_name="Vijay Nagar", city="Indore"),
            LocalityAlias(alias="vijaynagar", canonical_name="Vijay Nagar", city="Indore"),
            LocalityAlias(alias="MG Rd", canonical_name="MG Road", city="Indore"),
            LocalityAlias(alias="mahatma gandhi road", canonical_name="MG Road", city="Indore"),
            LocalityAlias(alias="rnt", canonical_name="RNT Marg", city="Indore"),
            LocalityAlias(alias="ring road", canonical_name="AB Road", city="Indore"),
            LocalityAlias(alias="bypass", canonical_name="Bypass Road", city="Indore"),
            LocalityAlias(alias="scheme 54", canonical_name="Scheme No. 54", city="Indore"),
            LocalityAlias(alias="scheme54", canonical_name="Scheme No. 54", city="Indore"),
            LocalityAlias(alias="scheme 78", canonical_name="Scheme No. 78", city="Indore"),
            LocalityAlias(alias="bhanwar kuan", canonical_name="Bhanwarkuan", city="Indore"),
            LocalityAlias(alias="bhanwarkua", canonical_name="Bhanwarkuan", city="Indore"),
        ]
        
        session.add_all(landmarks)
        session.add_all(aliases)
        session.commit()
        print("Database seeded with sample data.")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        close_db(session)
