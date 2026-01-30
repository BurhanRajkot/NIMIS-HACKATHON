"""
Explanation service - generates human-readable explanations for predictions.
"""


class ExplanationService:
    """
    Generates transparent explanations for address analysis results.
    """
    
    def __init__(self):
        """Initialize the explanation service."""
        pass
    
    def generate_explanation(self, parsed_address, landmark_matches, geocode_result, confidence_result):
        """
        Generate a human-readable explanation for the prediction.
        
        Args:
            parsed_address: Dictionary from AddressParser
            landmark_matches: List of matched landmarks
            geocode_result: Dictionary from Geocoder
            confidence_result: Dictionary from ConfidenceService
            
        Returns:
            Dictionary with explanation components
        """
        explanation = {
            'landmarks_used': self._extract_landmark_names(landmark_matches),
            'direction_interpreted': self._get_primary_direction(parsed_address),
            'method': geocode_result.get('method', 'rule-based'),
            'reasoning': self._generate_reasoning(
                parsed_address, landmark_matches, geocode_result, confidence_result
            ),
            'confidence_factors': self._explain_confidence(confidence_result)
        }
        
        return explanation
    
    def _extract_landmark_names(self, landmark_matches):
        """
        Extract landmark names from matches.
        
        Args:
            landmark_matches: List of matched landmarks
            
        Returns:
            List of landmark names
        """
        return [match['landmark'].name for match in landmark_matches]
    
    def _get_primary_direction(self, parsed_address):
        """
        Get the primary direction from parsed address.
        
        Args:
            parsed_address: Dictionary from AddressParser
            
        Returns:
            Primary direction string or None
        """
        directions = parsed_address.get('directions', [])
        return directions[0] if directions else None
    
    def _generate_reasoning(self, parsed_address, landmark_matches, geocode_result, confidence_result):
        """
        Generate step-by-step reasoning.
        
        Args:
            parsed_address: Dictionary from AddressParser
            landmark_matches: List of matched landmarks
            geocode_result: Dictionary from Geocoder
            confidence_result: Dictionary from ConfidenceService
            
        Returns:
            List of reasoning steps
        """
        steps = []
        
        # Step 1: Address parsing
        extracted = parsed_address.get('landmarks', [])
        if extracted:
            steps.append(f"Extracted {len(extracted)} potential landmark reference(s) from address: {', '.join(extracted)}")
        else:
            steps.append("No clear landmark references found in address")
        
        # Step 2: Direction extraction
        directions = parsed_address.get('directions', [])
        if directions:
            steps.append(f"Identified directional indicators: {', '.join(directions)}")
        
        # Step 3: Lane/house number
        lane = parsed_address.get('lane_number')
        house = parsed_address.get('house_number')
        if lane or house:
            details = []
            if lane:
                details.append(f"lane {lane}")
            if house:
                details.append(f"house #{house}")
            steps.append(f"Extracted specific identifiers: {', '.join(details)}")
        
        # Step 4: Landmark matching
        if landmark_matches:
            match_details = []
            for match in landmark_matches[:3]:
                lm = match['landmark']
                score = match['match_score']
                match_details.append(f"{lm.name} ({score:.0%} match)")
            steps.append(f"Matched to known landmarks: {', '.join(match_details)}")
        else:
            steps.append("No exact landmark matches found in database")
        
        # Step 5: Geocoding method
        method = geocode_result.get('method', 'unknown')
        accuracy = geocode_result.get('accuracy', 'unknown')
        steps.append(f"Applied geocoding method: {method} (accuracy: {accuracy})")
        
        # Step 6: Confidence
        level = confidence_result.get('level', 'UNKNOWN')
        score = confidence_result.get('score', 0)
        steps.append(f"Calculated confidence: {score:.0%} ({level})")
        
        return steps
    
    def _explain_confidence(self, confidence_result):
        """
        Explain confidence score breakdown.
        
        Args:
            confidence_result: Dictionary from ConfidenceService
            
        Returns:
            Dictionary explaining each factor
        """
        breakdown = confidence_result.get('breakdown', {})
        
        explanations = {}
        
        if 'landmark_match' in breakdown:
            score = breakdown['landmark_match']
            if score >= 0.8:
                explanations['landmark_match'] = f"Strong landmark match ({score:.0%})"
            elif score >= 0.5:
                explanations['landmark_match'] = f"Moderate landmark match ({score:.0%})"
            else:
                explanations['landmark_match'] = f"Weak/no landmark match ({score:.0%})"
        
        if 'address_completeness' in breakdown:
            score = breakdown['address_completeness']
            if score >= 0.7:
                explanations['address_completeness'] = f"Address has sufficient detail ({score:.0%})"
            else:
                explanations['address_completeness'] = f"Address lacks complete details ({score:.0%})"
        
        if 'direction_clarity' in breakdown:
            score = breakdown['direction_clarity']
            if score >= 0.7:
                explanations['direction_clarity'] = f"Clear directional references ({score:.0%})"
            else:
                explanations['direction_clarity'] = f"Ambiguous or missing directions ({score:.0%})"
        
        if 'delivery_history' in breakdown:
            score = breakdown['delivery_history']
            if score >= 0.7:
                explanations['delivery_history'] = f"Area has good delivery history ({score:.0%})"
            else:
                explanations['delivery_history'] = f"Limited delivery data in area ({score:.0%})"
        
        if 'geocoding_accuracy' in breakdown:
            score = breakdown['geocoding_accuracy']
            explanations['geocoding_accuracy'] = f"Geocoding accuracy: {score:.0%}"
        
        return explanations
    
    def generate_summary(self, confidence_result, landmark_matches):
        """
        Generate a brief summary of the prediction.
        
        Args:
            confidence_result: Dictionary from ConfidenceService
            landmark_matches: List of matched landmarks
            
        Returns:
            Summary string
        """
        level = confidence_result.get('level', 'UNKNOWN')
        score = confidence_result.get('score', 0)
        
        if not landmark_matches:
            return f"Location estimated with {level} confidence ({score:.0%}) using city-level approximation."
        
        primary_landmark = landmark_matches[0]['landmark'].name
        
        if level == 'HIGH':
            return f"Location identified near {primary_landmark} with {level} confidence ({score:.0%})."
        elif level == 'MEDIUM':
            return f"Location estimated near {primary_landmark} with {level} confidence ({score:.0%}). Manual verification recommended."
        else:
            return f"Location approximated near {primary_landmark} with {level} confidence ({score:.0%}). Delivery agent should confirm on ground."
