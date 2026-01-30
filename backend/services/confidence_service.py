"""
Confidence scoring service - calculates prediction confidence.
"""

from config.settings import Config


class ConfidenceService:
    """
    Calculates confidence scores for address predictions.
    """
    
    def __init__(self, db_session=None):
        """
        Initialize the confidence service.
        
        Args:
            db_session: Database session for historical lookups
        """
        self.db_session = db_session
        self.config = Config()
    
    def calculate_confidence(self, parsed_address, landmark_matches, geocode_result, city):
        """
        Calculate overall confidence score for a prediction.
        
        Args:
            parsed_address: Dictionary from AddressParser
            landmark_matches: List of matched landmarks
            geocode_result: Dictionary from Geocoder
            city: City name
            
        Returns:
            Dictionary with score and level
        """
        scores = []
        weights = []
        
        # 1. Landmark match quality (weight: 40%)
        landmark_score = self._calculate_landmark_score(landmark_matches)
        scores.append(landmark_score)
        weights.append(0.4)
        
        # 2. Address completeness (weight: 20%)
        completeness_score = self._calculate_completeness_score(parsed_address)
        scores.append(completeness_score)
        weights.append(0.2)
        
        # 3. Direction clarity (weight: 15%)
        direction_score = self._calculate_direction_score(parsed_address)
        scores.append(direction_score)
        weights.append(0.15)
        
        # 4. Delivery history density (weight: 15%)
        history_score = self._calculate_history_score(geocode_result, city)
        scores.append(history_score)
        weights.append(0.15)
        
        # 5. Geocoding accuracy (weight: 10%)
        accuracy_score = self._calculate_accuracy_score(geocode_result)
        scores.append(accuracy_score)
        weights.append(0.1)
        
        # Calculate weighted average
        total_score = sum(s * w for s, w in zip(scores, weights))
        
        # Determine confidence level
        level = self._determine_level(total_score)
        
        return {
            'score': round(total_score, 2),
            'level': level,
            'breakdown': {
                'landmark_match': round(landmark_score, 2),
                'address_completeness': round(completeness_score, 2),
                'direction_clarity': round(direction_score, 2),
                'delivery_history': round(history_score, 2),
                'geocoding_accuracy': round(accuracy_score, 2)
            }
        }
    
    def _calculate_landmark_score(self, landmark_matches):
        """
        Score based on landmark match quality.
        
        Args:
            landmark_matches: List of matched landmarks
            
        Returns:
            Score between 0 and 1
        """
        if not landmark_matches:
            return 0.0
        
        # Use best match score
        best_score = landmark_matches[0]['match_score']
        
        # Bonus for multiple matches
        match_count_bonus = min(len(landmark_matches) * 0.1, 0.2)
        
        return min(best_score + match_count_bonus, 1.0)
    
    def _calculate_completeness_score(self, parsed_address):
        """
        Score based on how complete the parsed address is.
        
        Args:
            parsed_address: Dictionary from AddressParser
            
        Returns:
            Score between 0 and 1
        """
        score = 0.0
        
        # Has landmarks (30%)
        if parsed_address.get('landmarks'):
            score += 0.3
        
        # Has lane/house number (25%)
        if parsed_address.get('lane_number') or parsed_address.get('house_number'):
            score += 0.25
        
        # Has locality (25%)
        if parsed_address.get('locality'):
            score += 0.25
        
        # Has multiple components (20%)
        components = parsed_address.get('components', [])
        if len(components) >= 2:
            score += 0.1
        if len(components) >= 3:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_direction_score(self, parsed_address):
        """
        Score based on directional clarity.
        
        Args:
            parsed_address: Dictionary from AddressParser
            
        Returns:
            Score between 0 and 1
        """
        directions = parsed_address.get('directions', [])
        landmarks = parsed_address.get('landmarks', [])
        
        if not directions:
            # No direction keywords - neutral score
            return 0.5
        
        if len(directions) == 1 and len(landmarks) >= 1:
            # Clear single direction with landmark
            return 0.9
        
        if len(directions) > 1 and len(landmarks) >= len(directions):
            # Multiple directions with matching landmarks
            return 0.8
        
        if len(directions) > len(landmarks):
            # More directions than landmarks - confusing
            return 0.3
        
        return 0.6
    
    def _calculate_history_score(self, geocode_result, city):
        """
        Score based on delivery history in the area.
        
        Args:
            geocode_result: Dictionary from Geocoder
            city: City name
            
        Returns:
            Score between 0 and 1
        """
        from database.models import DeliveryHistory
        
        if not self.db_session:
            return 0.5  # Neutral if no DB
        
        latitude = geocode_result.get('latitude')
        longitude = geocode_result.get('longitude')
        
        if not latitude or not longitude:
            return 0.3
        
        try:
            # Count successful deliveries nearby
            radius = 0.003  # ~300m
            
            count = self.db_session.query(DeliveryHistory).filter(
                DeliveryHistory.city.ilike(city),
                DeliveryHistory.delivery_success == True,
                DeliveryHistory.latitude.between(latitude - radius, latitude + radius),
                DeliveryHistory.longitude.between(longitude - radius, longitude + radius)
            ).count()
            
            if count >= 10:
                return 0.95
            elif count >= 5:
                return 0.8
            elif count >= 2:
                return 0.6
            else:
                return 0.4
            
        except Exception:
            return 0.5
    
    def _calculate_accuracy_score(self, geocode_result):
        """
        Score based on geocoding accuracy.
        
        Args:
            geocode_result: Dictionary from Geocoder
            
        Returns:
            Score between 0 and 1
        """
        accuracy = geocode_result.get('accuracy', 'low')
        
        accuracy_scores = {
            'high': 0.95,
            'medium': 0.7,
            'low': 0.4
        }
        
        return accuracy_scores.get(accuracy, 0.5)
    
    def _determine_level(self, score):
        """
        Determine confidence level from score.
        
        Args:
            score: Confidence score
            
        Returns:
            Confidence level string
        """
        if score >= self.config.CONFIDENCE_HIGH:
            return 'HIGH'
        elif score >= self.config.CONFIDENCE_MEDIUM:
            return 'MEDIUM'
        else:
            return 'LOW'
