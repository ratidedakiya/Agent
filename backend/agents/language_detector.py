import re
import logging
from typing import Dict, List, Optional, Tuple
from models.schemas import Language

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Language detection and text normalization agent"""
    
    def __init__(self):
        # Language detection patterns
        self.language_patterns = {
            Language.ENGLISH: {
                'indicators': ['the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'had'],
                'contractions': ["don't", "won't", "can't", "isn't", "aren't", "wasn't", "weren't"],
                'script': 'latin'
            },
            Language.HINDI: {
                'indicators': ['है', 'हैं', 'था', 'थे', 'था', 'कर', 'के', 'को', 'से', 'में'],
                'contractions': [],
                'script': 'devanagari'
            },
            Language.GUJARATI: {
                'indicators': ['છે', 'છો', 'હતા', 'હતો', 'કર', 'કે', 'કો', 'સે', 'માં'],
                'contractions': [],
                'script': 'gujarati'
            },
            Language.SPANISH: {
                'indicators': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se'],
                'contractions': ["del", "al"],
                'script': 'latin'
            },
            Language.FRENCH: {
                'indicators': ['le', 'la', 'de', 'que', 'et', 'à', 'en', 'un', 'est', 'se'],
                'contractions': ["du", "au", "des", "aux"],
                'script': 'latin'
            }
        }
        
        # Text normalization patterns
        self.normalization_patterns = {
            Language.ENGLISH: {
                'contractions': {
                    r"don't": "do not",
                    r"won't": "will not",
                    r"can't": "cannot",
                    r"isn't": "is not",
                    r"aren't": "are not",
                    r"wasn't": "was not",
                    r"weren't": "were not",
                    r"haven't": "have not",
                    r"hasn't": "has not",
                    r"hadn't": "had not",
                    r"wouldn't": "would not",
                    r"couldn't": "could not",
                    r"shouldn't": "should not",
                    r"i'm": "i am",
                    r"you're": "you are",
                    r"he's": "he is",
                    r"she's": "she is",
                    r"it's": "it is",
                    r"we're": "we are",
                    r"they're": "they are",
                    r"i've": "i have",
                    r"you've": "you have",
                    r"we've": "we have",
                    r"they've": "they have",
                    r"i'll": "i will",
                    r"you'll": "you will",
                    r"he'll": "he will",
                    r"she'll": "she will",
                    r"it'll": "it will",
                    r"we'll": "we will",
                    r"they'll": "they will"
                },
                'abbreviations': {
                    r"\bmath\b": "mathematics",
                    r"\bsci\b": "science",
                    r"\bprof\b": "professor",
                    r"\bdr\b": "doctor",
                    r"\bmr\b": "mister",
                    r"\bmrs\b": "missus",
                    r"\bms\b": "miss"
                }
            },
            Language.SPANISH: {
                'contractions': {
                    r"del": "de el",
                    r"al": "a el"
                },
                'abbreviations': {
                    r"\bmatemáticas\b": "matemáticas",
                    r"\bciencias\b": "ciencias"
                }
            },
            Language.FRENCH: {
                'contractions': {
                    r"du": "de le",
                    r"au": "à le",
                    r"des": "de les",
                    r"aux": "à les"
                },
                'abbreviations': {
                    r"\bmaths\b": "mathématiques",
                    r"\bsciences\b": "sciences"
                }
            }
        }
    
    async def detect_language(self, text: str, hint: Optional[Language] = None) -> Tuple[Language, float]:
        """Detect the language of the given text with confidence score"""
        try:
            if not text.strip():
                return hint or Language.ENGLISH, 0.0
            
            text_lower = text.lower()
            scores = {}
            
            # Check each language
            for lang, config in self.language_patterns.items():
                score = 0.0
                total_indicators = len(config['indicators'])
                
                # Count indicator words
                for indicator in config['indicators']:
                    if indicator in text_lower:
                        score += 1.0
                
                # Normalize score
                if total_indicators > 0:
                    score = score / total_indicators
                
                # Check script patterns
                if config['script'] == 'devanagari':
                    if any('\u0900' <= char <= '\u097F' for char in text):
                        score += 0.3
                elif config['script'] == 'gujarati':
                    if any('\u0A80' <= char <= '\u0AFF' for char in text):
                        score += 0.3
                elif config['script'] == 'latin':
                    if all(ord(char) < 128 for char in text):
                        score += 0.2
                
                scores[lang] = score
            
            # Find best match
            best_lang = max(scores, key=scores.get)
            confidence = scores[best_lang]
            
            # If hint provided and confidence is close, prefer hint
            if hint and scores.get(hint, 0) >= confidence * 0.8:
                best_lang = hint
                confidence = scores[hint]
            
            logger.info(f"Detected language: {best_lang} (confidence: {confidence:.2f})")
            return best_lang, confidence
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return hint or Language.ENGLISH, 0.0
    
    async def normalize_text(self, text: str, language: Language) -> str:
        """Normalize text by expanding contractions and standardizing abbreviations"""
        try:
            if not text.strip():
                return text
            
            normalized_text = text
            
            # Get normalization patterns for the language
            patterns = self.normalization_patterns.get(language, {})
            
            # Expand contractions
            contractions = patterns.get('contractions', {})
            for contraction, expansion in contractions.items():
                normalized_text = re.sub(contraction, expansion, normalized_text, flags=re.IGNORECASE)
            
            # Expand abbreviations
            abbreviations = patterns.get('abbreviations', {})
            for abbrev, expansion in abbreviations.items():
                normalized_text = re.sub(abbrev, expansion, normalized_text, flags=re.IGNORECASE)
            
            # Clean up extra spaces
            normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
            
            logger.debug(f"Normalized text: '{text[:50]}...' -> '{normalized_text[:50]}...'")
            return normalized_text
            
        except Exception as e:
            logger.error(f"Error normalizing text: {e}")
            return text
    
    async def transliterate_text(self, text: str, from_script: str, to_script: str) -> str:
        """Transliterate text between different scripts"""
        try:
            # This is a simplified transliteration
            # In production, use a proper transliteration library like indic-transliteration
            
            if from_script == 'devanagari' and to_script == 'latin':
                # Basic Devanagari to Latin transliteration
                devanagari_to_latin = {
                    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ii', 'उ': 'u', 'ऊ': 'uu',
                    'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
                    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
                    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
                    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
                    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
                    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
                    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
                    'ष': 'sh', 'स': 's', 'ह': 'h'
                }
                
                transliterated = ''
                for char in text:
                    transliterated += devanagari_to_latin.get(char, char)
                return transliterated
            
            elif from_script == 'gujarati' and to_script == 'latin':
                # Basic Gujarati to Latin transliteration
                gujarati_to_latin = {
                    'અ': 'a', 'આ': 'aa', 'ઇ': 'i', 'ઈ': 'ii', 'ઉ': 'u', 'ઊ': 'uu',
                    'એ': 'e', 'ઐ': 'ai', 'ઓ': 'o', 'ઔ': 'au',
                    'ક': 'k', 'ખ': 'kh', 'ગ': 'g', 'ઘ': 'gh', 'ઙ': 'ng',
                    'ચ': 'ch', 'છ': 'chh', 'જ': 'j', 'ઝ': 'jh', 'ઞ': 'ny',
                    'ટ': 't', 'ઠ': 'th', 'ડ': 'd', 'ઢ': 'dh', 'ણ': 'n',
                    'ત': 't', 'થ': 'th', 'દ': 'd', 'ધ': 'dh', 'ન': 'n',
                    'પ': 'p', 'ફ': 'ph', 'બ': 'b', 'ભ': 'bh', 'મ': 'm',
                    'ય': 'y', 'ર': 'r', 'લ': 'l', 'વ': 'v', 'શ': 'sh',
                    'ષ': 'sh', 'સ': 's', 'હ': 'h'
                }
                
                transliterated = ''
                for char in text:
                    transliterated += gujarati_to_latin.get(char, char)
                return transliterated
            
            # If no transliteration needed or supported, return original
            return text
            
        except Exception as e:
            logger.error(f"Error transliterating text: {e}")
            return text
    
    async def detect_dialect(self, text: str, language: Language) -> Optional[str]:
        """Detect dialect or regional variation of the language"""
        try:
            if language == Language.ENGLISH:
                # Detect English dialects
                if any(word in text.lower() for word in ['colour', 'favour', 'behaviour']):
                    return 'british'
                elif any(word in text.lower() for word in ['y\'all', 'ain\'t', 'fixin\'']):
                    return 'southern_american'
                elif any(word in text.lower() for word in ['eh', 'aboot', 'soory']):
                    return 'canadian'
                else:
                    return 'american'
            
            elif language == Language.SPANISH:
                # Detect Spanish dialects
                if any(word in text.lower() for word in ['vos', 'che', 'boludo']):
                    return 'argentinian'
                elif any(word in text.lower() for word in ['vale', 'tío', 'guay']):
                    return 'spain'
                elif any(word in text.lower() for word in ['chido', 'güey', 'órale']):
                    return 'mexican'
                else:
                    return 'general'
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting dialect: {e}")
            return None
    
    async def get_language_info(self, language: Language) -> Dict[str, Any]:
        """Get information about a specific language"""
        try:
            config = self.language_patterns.get(language, {})
            return {
                'language': language,
                'script': config.get('script', 'unknown'),
                'indicators': config.get('indicators', []),
                'contractions': config.get('contractions', []),
                'has_normalization': language in self.normalization_patterns
            }
        except Exception as e:
            logger.error(f"Error getting language info: {e}")
            return {}
    
    async def validate_text(self, text: str, language: Language) -> Dict[str, Any]:
        """Validate text for language-specific issues"""
        try:
            issues = []
            suggestions = []
            
            # Check for mixed scripts
            if language in [Language.HINDI, Language.GUJARATI]:
                # Check for Latin characters in Indic text
                latin_chars = sum(1 for char in text if ord(char) < 128)
                if latin_chars > len(text) * 0.3:
                    issues.append('mixed_script')
                    suggestions.append('Consider using consistent script')
            
            # Check for common misspellings
            if language == Language.ENGLISH:
                common_misspellings = {
                    'recieve': 'receive',
                    'seperate': 'separate',
                    'definately': 'definitely',
                    'occured': 'occurred'
                }
                
                for misspelling, correction in common_misspellings.items():
                    if misspelling in text.lower():
                        issues.append('misspelling')
                        suggestions.append(f'Did you mean "{correction}"?')
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'suggestions': suggestions
            }
            
        except Exception as e:
            logger.error(f"Error validating text: {e}")
            return {'valid': True, 'issues': [], 'suggestions': []}