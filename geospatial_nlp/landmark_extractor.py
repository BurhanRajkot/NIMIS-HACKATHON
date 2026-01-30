"""
Landmark Extraction and Matching for Indian Addresses.

Extracts location-relevant entities from addresses:
- Named landmarks (temples, stations, markets)
- Positional references (near, behind, opposite)
- Building names and complexes
- Area/locality names

Approach: Hybrid system combining:
1. Pattern-based extraction (fast, high precision for known patterns)
2. Lightweight NER fallback (spaCy) for catching novel entities
3. Fuzzy matching for landmark name normalization

This avoids heavy model training while capturing most landmarks accurately.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Conditional import for spaCy (optional dependency)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

# Conditional import for fuzzy matching
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

from .utils import load_landmark_patterns, clean_text


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ExtractedLandmark:
    """
    Represents an extracted landmark with metadata.
    
    Attributes:
        text: Original text span that was identified as a landmark
        category: Type of landmark (religious, transport, commercial, etc.)
        normalized: Cleaned/normalized form of the landmark name
        position: Positional relation (near, behind, opposite, etc.)
        confidence: Extraction confidence score (0-1)
        start: Start character offset in original text
        end: End character offset in original text
    """
    text: str
    category: str
    normalized: str
    position: Optional[str] = None
    confidence: float = 1.0
    start: int = 0
    end: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "category": self.category,
            "normalized": self.normalized,
            "position": self.position,
            "confidence": self.confidence,
            "span": [self.start, self.end],
        }


# =============================================================================
# PATTERN DEFINITIONS
# =============================================================================

# Positional keywords that indicate a landmark reference
POSITIONAL_PATTERNS = {
    "near": ["near", "nr", "close to", "beside", "by", "next to", "nxt to", "adjacent"],
    "opposite": ["opposite", "opp", "opp to", "facing", "across from", "in front of"],
    "behind": ["behind", "bhnd", "b/h", "back of", "at back", "rear of"],
    "above": ["above", "over", "upstairs from", "on top of"],
    "below": ["below", "under", "downstairs from", "beneath"],
    "inside": ["inside", "within", "in", "at"],
}

# Compile positional patterns for efficient matching
_POSITIONAL_RE = re.compile(
    r'\b(' + '|'.join(
        re.escape(p) for patterns in POSITIONAL_PATTERNS.values() for p in patterns
    ) + r')\b',
    re.IGNORECASE
)

# Landmark type indicators with their categories
LANDMARK_INDICATORS = {
    "religious": [
        r"(?:shri|shree|sri)?\s*\w+\s*(?:mandir|temple|devasthan)",
        r"(?:jama|jamia)?\s*\w*\s*(?:masjid|mosque|dargah)",
        r"\w+\s*(?:church|cathedral|chapel)",
        r"(?:gurudwara|gurdwara)\s*(?:sahib)?",
        r"\w+\s*(?:math|mutt|ashram|ashrama)",
    ],
    "transport": [
        r"\w+\s*(?:railway|rly)\s*(?:station|stn)",
        r"\w+\s*(?:bus)\s*(?:stand|stop|station|depot)",
        r"\w+\s*(?:metro)\s*(?:station|stn)?",
        r"\w+\s*(?:airport|airfield)",
        r"\w+\s*(?:junction|jn|jcn)",
    ],
    "commercial": [
        r"\w+\s*(?:market|mkt|bazaar|bazar|mandi|haat)",
        r"\w+\s*(?:mall|plaza|arcade|complex)",
        r"\w+\s*(?:hotel|lodge|inn|dhaba)",
        r"\w+\s*(?:shop|store|showroom|emporium)",
        r"\w+\s*(?:bank|atm)",
        r"\w+\s*(?:petrol|gas)\s*(?:pump|station|bunk)",
    ],
    "education": [
        r"\w+\s*(?:school|vidyalaya|vidya\s*mandir|pathshala)",
        r"\w+\s*(?:college|mahavidyalaya)",
        r"\w+\s*(?:university|vishwavidyalaya)",
        r"\w+\s*(?:institute|institution|academy)",
        r"\w+\s*(?:coaching|classes|tuition)",
    ],
    "health": [
        r"\w+\s*(?:hospital|hosp|nursing\s*home)",
        r"\w+\s*(?:clinic|dispensary|polyclinic)",
        r"\w+\s*(?:medical|medicals|pharmacy|chemist)",
        r"(?:dr|doctor)\s*\w+(?:'s)?\s*(?:clinic|hospital)?",
    ],
    "government": [
        r"\w*\s*(?:police)\s*(?:station|chowki|thana)",
        r"\w*\s*(?:post)\s*(?:office|o)",
        r"\w*\s*(?:court|kacheri|kachahri)",
        r"(?:collector|tehsil|taluka|block)\s*(?:office)?",
        r"\w+\s*(?:bhavan|bhawan|sadan)\s*(?:government|govt)?",
    ],
    "infrastructure": [
        r"\w+\s*(?:bridge|pul|setu|overbridge|flyover)",
        r"\w+\s*(?:signal|traffic\s*light)",
        r"\w+\s*(?:chowk|chawk|chauk|circle|square|roundabout)",
        r"\w+\s*(?:naka|naaka|toll|gate|crossing)",
        r"\w+\s*(?:park|garden|baug|bagh|maidan|ground)",
    ],
    "residential": [
        r"\w+\s*(?:society|soc|complex|apartment|apts|tower)",
        r"\w+\s*(?:nagar|puram|colony|enclave|vihar|kunj)",
        r"\w+\s*(?:chawl|chawls|tenement)",
        r"\w+\s*(?:layout|phase|sector|block)",
    ],
}


# =============================================================================
# LANDMARK EXTRACTOR CLASS
# =============================================================================

class LandmarkExtractor:
    """
    Extracts landmarks from address text using hybrid approach.
    
    Extraction pipeline:
    1. Pattern matching for known landmark types
    2. Positional context detection (near, opposite, behind)
    3. Optional NER for catching unmarked entities
    4. Fuzzy matching for normalization
    
    This balanced approach gives good coverage without requiring
    extensive training data or large models.
    """
    
    def __init__(
        self,
        use_ner: bool = False,  # Disabled by default for speed
        use_fuzzy: bool = True,
        min_confidence: float = 0.5,
    ):
        """
        Initialize landmark extractor.
        
        Args:
            use_ner: Whether to use spaCy NER (requires spacy + model)
            use_fuzzy: Whether to use fuzzy matching for normalization
            min_confidence: Minimum confidence threshold for extracted landmarks
        """
        self.use_ner = use_ner and SPACY_AVAILABLE
        self.use_fuzzy = use_fuzzy and RAPIDFUZZ_AVAILABLE
        self.min_confidence = min_confidence
        
        # Load NER model if enabled
        self._nlp = None
        if self.use_ner:
            self._load_spacy_model()
        
        # Compile regex patterns
        self._compile_patterns()
        
        # Load known landmarks for fuzzy matching
        self._known_landmarks = self._load_known_landmarks()
    
    def _load_spacy_model(self):
        """
        Load spaCy model for NER.
        
        ML Note: We use en_core_web_sm (12MB) as it's lightweight and provides
        decent NER for English. For better Hindi/regional language support,
        consider training a custom model or using multilingual transformers.
        """
        try:
            self._nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model 'en_core_web_sm' not found. NER disabled.")
            self.use_ner = False
    
    def _compile_patterns(self):
        """
        Compile regex patterns for landmark detection.
        
        ML Note: Pre-compiling regex patterns improves performance significantly
        when processing many addresses. Patterns are category-specific to enable
        accurate classification without needing a trained classifier.
        """
        self._patterns = {}
        for category, patterns in LANDMARK_INDICATORS.items():
            combined = '|'.join(f'({p})' for p in patterns)
            self._patterns[category] = re.compile(combined, re.IGNORECASE)
    
    def _load_known_landmarks(self) -> Dict[str, List[str]]:
        """
        Load known landmark names for fuzzy matching.
        
        ML Note: This acts as a "knowledge base" for normalizing extracted
        landmarks. Fuzzy matching against known names helps standardize
        variations (e.g., "rly stn" -> "Railway Station").
        """
        return load_landmark_patterns()
    
    def extract(self, text: str) -> List[Dict]:
        """
        Extract landmarks from address text.
        
        Args:
            text: Normalized address text
            
        Returns:
            List of extracted landmark dictionaries
        """
        if not text:
            return []
        
        landmarks = []
        text_lower = text.lower()
        
        # Step 1: Extract landmarks using patterns
        pattern_results = self._extract_by_patterns(text_lower, text)
        landmarks.extend(pattern_results)
        
        # Step 2: Extract positional references
        positional_results = self._extract_positional_context(text_lower, text)
        landmarks.extend(positional_results)
        
        # Step 3: Use NER if enabled and few patterns matched
        if self.use_ner and len(landmarks) < 2:
            ner_results = self._extract_by_ner(text)
            # Add NER results that don't overlap with pattern results
            for ner_lm in ner_results:
                if not self._overlaps_existing(ner_lm, landmarks):
                    landmarks.append(ner_lm)
        
        # Step 4: Normalize and deduplicate
        landmarks = self._deduplicate(landmarks)
        
        # Step 5: Filter by confidence
        landmarks = [lm for lm in landmarks if lm.get("confidence", 1.0) >= self.min_confidence]
        
        return landmarks
    
    def _extract_by_patterns(self, text_lower: str, original_text: str) -> List[Dict]:
        """
        Extract landmarks using regex patterns.
        
        ML Note: Pattern matching is our primary extraction method because:
        1. High precision - patterns are crafted for known landmark types
        2. Fast - O(n) scan, no model inference needed
        3. Interpretable - easy to debug and extend with new patterns
        Confidence is set to 0.9 (high) since pattern matches are reliable.
        """
        results = []
        
        for category, pattern in self._patterns.items():
            for match in pattern.finditer(text_lower):
                # Get the matched text from original (preserving case)
                start, end = match.span()
                matched_text = original_text[start:end].strip()
                
                # Skip very short matches (likely false positives)
                if len(matched_text) < 3:
                    continue
                
                landmark = ExtractedLandmark(
                    text=matched_text,
                    category=category,
                    normalized=self._normalize_landmark(matched_text, category),
                    confidence=0.9,  # High confidence for pattern matches
                    start=start,
                    end=end,
                )
                results.append(landmark.to_dict())
        
        return results
    
    def _extract_positional_context(self, text_lower: str, original_text: str) -> List[Dict]:
        """
        Extract landmark references that follow positional keywords.
        
        Pattern: [positional_word] [landmark_phrase]
        Example: "near shiv temple" -> extracts "shiv temple" with position="near"
        """
        results = []
        
        for position, keywords in POSITIONAL_PATTERNS.items():
            for keyword in keywords:
                # Pattern: keyword followed by potential landmark
                # Capture words until delimiter (comma, hyphen, or end)
                pattern = rf'\b{re.escape(keyword)}\s+([^,\-\n]+?)(?:[,\-]|$)'
                
                for match in re.finditer(pattern, text_lower):
                    landmark_text = match.group(1).strip()
                    
                    # Skip if too short or looks like just a locality name
                    if len(landmark_text) < 4:
                        continue
                    
                    # Skip if it's just a number (like "near 100")
                    if landmark_text.replace(' ', '').isdigit():
                        continue
                    
                    # Get position in original text
                    full_start = match.start()
                    phrase_start = match.start(1)
                    phrase_end = match.end(1)
                    
                    # Check if this wasn't already captured by pattern matching
                    landmark = ExtractedLandmark(
                        text=original_text[phrase_start:phrase_end].strip(),
                        category="referenced",  # Unknown category, discovered by position
                        normalized=self._normalize_landmark(landmark_text, "referenced"),
                        position=position,
                        confidence=0.75,  # Slightly lower confidence
                        start=phrase_start,
                        end=phrase_end,
                    )
                    results.append(landmark.to_dict())
        
        return results
    
    def _extract_by_ner(self, text: str) -> List[Dict]:
        """
        Extract entities using spaCy NER (fallback method).
        
        ML Note: NER acts as a safety net to catch landmarks that don't match
        our predefined patterns. It's useful for:
        - Named entities we haven't explicitly patterned (e.g., "Taj Mahal")
        - Organization names that might be landmarks (e.g., "Infosys Campus")
        
        Confidence is set to 0.6 (lower) since NER can produce false positives,
        especially for Indian addresses with transliterated names.
        
        Entity types used: GPE (cities), LOC (locations), FAC (facilities), ORG (orgs)
        """
        if not self._nlp:
            return []
        
        results = []
        doc = self._nlp(text)
        
        # Relevant entity types for landmarks
        relevant_types = {"GPE", "LOC", "FAC", "ORG"}
        
        for ent in doc.ents:
            if ent.label_ in relevant_types:
                # Map NER label to our categories
                category_map = {
                    "GPE": "location",
                    "LOC": "location", 
                    "FAC": "infrastructure",
                    "ORG": "organization",
                }
                
                landmark = ExtractedLandmark(
                    text=ent.text,
                    category=category_map.get(ent.label_, "other"),
                    normalized=self._normalize_landmark(ent.text, "ner"),
                    confidence=0.6,  # Lower confidence for NER
                    start=ent.start_char,
                    end=ent.end_char,
                )
                results.append(landmark.to_dict())
        
        return results
    
    def _normalize_landmark(self, text: str, category: str) -> str:
        """
        Normalize landmark text to canonical form.
        
        ML Note: Normalization is crucial for downstream matching. We use:
        1. Text cleaning (lowercase, whitespace normalization)
        2. Fuzzy matching with 80% threshold against known landmarks
        
        The 80% threshold balances catching variations ("rly station" -> "railway station")
        while avoiding false matches. Uses token_sort_ratio which handles word order.
        """
        cleaned = clean_text(text)
        
        if not self.use_fuzzy or not cleaned:
            return cleaned.title()
        
        # Try to match against known landmarks in this category
        known = self._known_landmarks.get(category, [])
        if not known:
            # Try all categories
            known = [lm for lms in self._known_landmarks.values() for lm in lms]
        
        if known:
            # Find best match using fuzzy matching
            result = process.extractOne(
                cleaned,
                known,
                scorer=fuzz.token_sort_ratio,
                score_cutoff=80  # Only accept matches with 80%+ similarity
            )
            if result:
                return result[0].title()
        
        return cleaned.title()
    
    def _overlaps_existing(self, new_landmark: Dict, existing: List[Dict]) -> bool:
        """
        Check if new landmark overlaps with any existing landmarks.
        
        ML Note: Overlap detection prevents extracting the same text span twice
        (e.g., pattern match and NER both finding "Railway Station"). We use
        character offsets rather than text matching for precision.
        """
        new_span = new_landmark.get("span", [0, 0])
        
        for lm in existing:
            existing_span = lm.get("span", [0, 0])
            # Check for overlap
            if (new_span[0] < existing_span[1] and new_span[1] > existing_span[0]):
                return True
        
        return False
    
    def _deduplicate(self, landmarks: List[Dict]) -> List[Dict]:
        """
        Remove duplicate landmarks, keeping higher confidence ones.
        
        ML Note: Deduplication is essential when using multiple extraction methods.
        We prioritize by confidence score (pattern > positional > NER) and use
        both span overlap and normalized text matching to catch duplicates.
        This ensures the final output has unique, high-quality landmarks.
        """
        if not landmarks:
            return []
        
        # Sort by confidence descending
        landmarks = sorted(landmarks, key=lambda x: x.get("confidence", 0), reverse=True)
        
        result = []
        seen_normalized = set()
        
        for lm in landmarks:
            normalized = lm.get("normalized", "").lower()
            
            # Skip if we've seen this normalized form
            if normalized in seen_normalized:
                continue
            
            # Skip if overlaps with higher confidence result
            if self._overlaps_existing(lm, result):
                continue
            
            result.append(lm)
            seen_normalized.add(normalized)
        
        return result


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def extract_landmarks(text: str, **kwargs) -> List[Dict]:
    """
    Convenience function to extract landmarks from text.
    
    Args:
        text: Address text (ideally normalized first)
        **kwargs: Options passed to LandmarkExtractor
        
    Returns:
        List of extracted landmark dictionaries
    """
    extractor = LandmarkExtractor(**kwargs)
    return extractor.extract(text)
