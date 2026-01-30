"""
Landmark service - matches addresses to known landmarks.
"""

from utils.text_utils import normalize_text, fuzzy_match_score, contains_any


class LandmarkService:
    """
    Handles landmark matching and retrieval from database.
    """
    
    # Minimum score threshold for fuzzy matching
    MIN_MATCH_SCORE = 0.3
    
    def __init__(self, db_session):
        """
        Initialize the landmark service.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
    
    def find_matching_landmarks(self, parsed_address, city):
        """
        Find landmarks matching the parsed address.
        
        Args:
            parsed_address: Dictionary from AddressParser
            city: City name for scoped search
            
        Returns:
            List of matched landmarks with scores
        """
        from database.models import Landmark
        
        extracted_landmarks = parsed_address.get('landmarks', [])
        if not extracted_landmarks:
            return []
        
        # Get all active landmarks for the city
        try:
            db_landmarks = self.db_session.query(Landmark).filter(
                Landmark.city.ilike(city),
                Landmark.is_active == True
            ).all()
        except Exception:
            return []
        
        matches = []
        
        for extracted in extracted_landmarks:
            best_match = None
            best_score = 0
            
            for db_landmark in db_landmarks:
                score = self._calculate_match_score(extracted, db_landmark)
                
                if score > best_score and score >= self.MIN_MATCH_SCORE:
                    best_score = score
                    best_match = db_landmark
            
            if best_match:
                matches.append({
                    'landmark': best_match,
                    'extracted_text': extracted,
                    'match_score': best_score
                })
        
        # Sort by match score descending
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches
    
    def _calculate_match_score(self, text, landmark):
        """
        Calculate match score between text and a landmark.
        
        Args:
            text: Extracted landmark text from address
            landmark: Landmark database object
            
        Returns:
            Match score between 0 and 1
        """
        text_normalized = normalize_text(text)
        name_normalized = normalize_text(landmark.name)
        
        # Exact match
        if text_normalized == name_normalized:
            return 1.0
        
        # Check if text contains landmark name or vice versa
        if text_normalized in name_normalized or name_normalized in text_normalized:
            shorter = min(len(text_normalized), len(name_normalized))
            longer = max(len(text_normalized), len(name_normalized))
            return 0.7 + (0.3 * shorter / longer)
        
        # Fuzzy match on name
        name_score = fuzzy_match_score(text, landmark.name)
        
        # Check keywords
        keywords = landmark.keywords.split(',') if landmark.keywords else []
        keyword_match = contains_any(text, keywords)
        keyword_score = 0.5 if keyword_match else 0
        
        # Check locality match
        locality_normalized = normalize_text(landmark.locality) if landmark.locality else ""
        locality_score = fuzzy_match_score(text, locality_normalized) * 0.3 if locality_normalized else 0
        
        # Combined score with weights
        combined_score = (name_score * 0.6) + (keyword_score * 0.25) + (locality_score * 0.15)
        
        return min(combined_score, 1.0)
    
    def get_landmarks_by_city(self, city):
        """
        Get all landmarks for a city.
        
        Args:
            city: City name
            
        Returns:
            List of landmark dictionaries
        """
        from database.models import Landmark
        
        try:
            landmarks = self.db_session.query(Landmark).filter(
                Landmark.city.ilike(city),
                Landmark.is_active == True
            ).order_by(Landmark.name).all()
            
            return [lm.to_dict() for lm in landmarks]
        except Exception:
            return []
    
    def get_landmark_by_id(self, landmark_id):
        """
        Get a specific landmark by ID.
        
        Args:
            landmark_id: Landmark ID
            
        Returns:
            Landmark dictionary or None
        """
        from database.models import Landmark
        
        try:
            landmark = self.db_session.query(Landmark).filter(
                Landmark.id == landmark_id
            ).first()
            
            return landmark.to_dict() if landmark else None
        except Exception:
            return None
    
    def search_landmarks(self, query, city=None):
        """
        Search landmarks by name or keywords.
        
        Args:
            query: Search query string
            city: Optional city filter
            
        Returns:
            List of matching landmark dictionaries
        """
        from database.models import Landmark
        
        try:
            q = self.db_session.query(Landmark).filter(
                Landmark.is_active == True
            )
            
            if city:
                q = q.filter(Landmark.city.ilike(city))
            
            # Search in name and keywords
            search_pattern = f"%{query}%"
            q = q.filter(
                (Landmark.name.ilike(search_pattern)) |
                (Landmark.keywords.ilike(search_pattern))
            )
            
            landmarks = q.order_by(Landmark.name).limit(20).all()
            
            return [lm.to_dict() for lm in landmarks]
        except Exception:
            return []
