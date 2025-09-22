import re
import logging
from typing import Dict, List, Optional, Any
from models.schemas import (
    Emotion, GestureTag, ResponseSynthesizerInput, ResponseSynthesizerOutput,
    Language, Persona
)

logger = logging.getLogger(__name__)

class ResponseSynthesizer:
    """Synthesizes responses with voice, emotion, and gesture metadata for avatar"""
    
    def __init__(self):
        # Voice style configurations
        self.voice_styles = {
            'friendly_male': {
                'pitch': 'medium',
                'rate': 'normal',
                'volume': 'medium',
                'tone': 'warm',
                'accent': 'neutral'
            },
            'friendly_female': {
                'pitch': 'high',
                'rate': 'normal',
                'volume': 'medium',
                'tone': 'warm',
                'accent': 'neutral'
            },
            'professional_male': {
                'pitch': 'low',
                'rate': 'slow',
                'volume': 'high',
                'tone': 'formal',
                'accent': 'neutral'
            },
            'professional_female': {
                'pitch': 'medium',
                'rate': 'slow',
                'volume': 'high',
                'tone': 'formal',
                'accent': 'neutral'
            },
            'encouraging_male': {
                'pitch': 'medium',
                'rate': 'fast',
                'volume': 'high',
                'tone': 'enthusiastic',
                'accent': 'neutral'
            },
            'encouraging_female': {
                'pitch': 'high',
                'rate': 'fast',
                'volume': 'high',
                'tone': 'enthusiastic',
                'accent': 'neutral'
            }
        }
        
        # Emotion-based text modifications
        self.emotion_modifiers = {
            Emotion.CALM: {
                'text_prefix': '',
                'text_suffix': '',
                'emphasis_words': [],
                'gesture_intensity': 'low'
            },
            Emotion.ENCOURAGING: {
                'text_prefix': 'Great! ',
                'text_suffix': ' Keep up the excellent work!',
                'emphasis_words': ['excellent', 'wonderful', 'fantastic', 'amazing'],
                'gesture_intensity': 'high'
            },
            Emotion.CORRECTIVE: {
                'text_prefix': 'Let me help you with that. ',
                'text_suffix': ' Does that make sense?',
                'emphasis_words': ['important', 'remember', 'note', 'key'],
                'gesture_intensity': 'medium'
            },
            Emotion.EXCITED: {
                'text_prefix': 'Excellent question! ',
                'text_suffix': ' This is really interesting!',
                'emphasis_words': ['exciting', 'fascinating', 'incredible', 'amazing'],
                'gesture_intensity': 'high'
            },
            Emotion.NEUTRAL: {
                'text_prefix': '',
                'text_suffix': '',
                'emphasis_words': [],
                'gesture_intensity': 'medium'
            }
        }
        
        # Gesture mapping based on content and emotion
        self.gesture_mapping = {
            GestureTag.AFFIRMATIVE: {
                'triggers': ['yes', 'correct', 'right', 'good', 'excellent', 'perfect'],
                'gesture': 'nod',
                'frequency': 'high'
            },
            GestureTag.CORRECTIVE: {
                'triggers': ['no', 'incorrect', 'wrong', 'mistake', 'error', 'try again'],
                'gesture': 'shake_head',
                'frequency': 'medium'
            },
            GestureTag.ILLUSTRATIVE: {
                'triggers': ['imagine', 'picture', 'visualize', 'see', 'look', 'example'],
                'gesture': 'point',
                'frequency': 'high'
            },
            GestureTag.QUESTIONING: {
                'triggers': ['?', 'what', 'how', 'why', 'when', 'where', 'do you'],
                'gesture': 'tilt_head',
                'frequency': 'medium'
            },
            GestureTag.POINTING: {
                'triggers': ['here', 'there', 'this', 'that', 'note', 'important'],
                'gesture': 'point',
                'frequency': 'high'
            }
        }
        
        # Emphasis detection patterns
        self.emphasis_patterns = [
            r'\*\*(.*?)\*\*',  # Bold text
            r'\*(.*?)\*',      # Italic text
            r'_(.*?)_',        # Underlined text
            r'`(.*?)`',        # Code/monospace
            r'"(.*?)"',        # Quoted text
            r'important',      # Important keyword
            r'key',           # Key keyword
            r'remember',      # Remember keyword
            r'note',          # Note keyword
        ]
    
    async def synthesize_response(
        self, 
        input_data: ResponseSynthesizerInput
    ) -> ResponseSynthesizerOutput:
        """Synthesize response with voice, emotion, and gesture metadata"""
        try:
            # Process text based on emotion
            processed_text = await self._process_text_for_emotion(
                input_data.text, 
                input_data.emotion
            )
            
            # Detect emphasis spans
            emphasis_spans = await self._detect_emphasis_spans(processed_text)
            
            # Determine gesture tag based on content
            gesture_tag = await self._determine_gesture_tag(
                processed_text, 
                input_data.gesture_tag
            )
            
            # Apply voice style modifications
            voice_style = await self._apply_voice_style(
                input_data.voice_style, 
                input_data.emotion
            )
            
            logger.info(f"Synthesized response with emotion: {input_data.emotion}, gesture: {gesture_tag}")
            
            return ResponseSynthesizerOutput(
                text=processed_text,
                voice_style=voice_style,
                language=input_data.language,
                emotion=input_data.emotion,
                gesture_tag=gesture_tag,
                emphasis_spans=emphasis_spans
            )
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")
            return ResponseSynthesizerOutput(
                text=input_data.text,
                voice_style=input_data.voice_style,
                language=input_data.language,
                emotion=input_data.emotion,
                gesture_tag=input_data.gesture_tag,
                emphasis_spans=[]
            )
    
    async def _process_text_for_emotion(
        self, 
        text: str, 
        emotion: Emotion
    ) -> str:
        """Process text to reflect the intended emotion"""
        try:
            emotion_config = self.emotion_modifiers.get(emotion, self.emotion_modifiers[Emotion.NEUTRAL])
            
            # Add prefix and suffix
            processed_text = emotion_config['text_prefix'] + text + emotion_config['text_suffix']
            
            # Add emphasis to key words
            emphasis_words = emotion_config['emphasis_words']
            for word in emphasis_words:
                if word in processed_text.lower():
                    # Find and emphasize the word
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    processed_text = pattern.sub(f'**{word}**', processed_text)
            
            # Clean up extra spaces
            processed_text = re.sub(r'\s+', ' ', processed_text).strip()
            
            return processed_text
            
        except Exception as e:
            logger.error(f"Error processing text for emotion: {e}")
            return text
    
    async def _detect_emphasis_spans(self, text: str) -> List[Dict[str, int]]:
        """Detect text spans that should be emphasized"""
        try:
            emphasis_spans = []
            
            for pattern in self.emphasis_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    start = match.start()
                    end = match.end()
                    content = match.group(1) if match.groups() else match.group(0)
                    
                    emphasis_spans.append({
                        'start': start,
                        'end': end,
                        'content': content,
                        'type': 'bold' if '**' in pattern else 'italic' if '*' in pattern else 'emphasis'
                    })
            
            # Sort by start position
            emphasis_spans.sort(key=lambda x: x['start'])
            
            return emphasis_spans
            
        except Exception as e:
            logger.error(f"Error detecting emphasis spans: {e}")
            return []
    
    async def _determine_gesture_tag(
        self, 
        text: str, 
        suggested_gesture: GestureTag
    ) -> GestureTag:
        """Determine the most appropriate gesture based on content"""
        try:
            text_lower = text.lower()
            gesture_scores = {}
            
            # Score each gesture based on trigger words
            for gesture, config in self.gesture_mapping.items():
                score = 0
                for trigger in config['triggers']:
                    if trigger in text_lower:
                        score += 1
                
                # Apply frequency weight
                frequency_weight = {'high': 2, 'medium': 1.5, 'low': 1}
                score *= frequency_weight.get(config['frequency'], 1)
                
                gesture_scores[gesture] = score
            
            # Find best gesture
            if gesture_scores and max(gesture_scores.values()) > 0:
                best_gesture = max(gesture_scores, key=gesture_scores.get)
                return best_gesture
            
            # Fall back to suggested gesture or default
            return suggested_gesture or GestureTag.AFFIRMATIVE
            
        except Exception as e:
            logger.error(f"Error determining gesture tag: {e}")
            return suggested_gesture or GestureTag.AFFIRMATIVE
    
    async def _apply_voice_style(
        self, 
        voice_style: str, 
        emotion: Emotion
    ) -> str:
        """Apply voice style modifications based on emotion"""
        try:
            base_style = self.voice_styles.get(voice_style, self.voice_styles['friendly_male'])
            
            # Modify based on emotion
            emotion_modifications = {
                Emotion.ENCOURAGING: {'rate': 'fast', 'volume': 'high'},
                Emotion.CALM: {'rate': 'slow', 'volume': 'low'},
                Emotion.EXCITED: {'rate': 'fast', 'volume': 'high'},
                Emotion.CORRECTIVE: {'rate': 'slow', 'volume': 'medium'},
                Emotion.NEUTRAL: {}  # No modifications
            }
            
            modifications = emotion_modifications.get(emotion, {})
            modified_style = {**base_style, **modifications}
            
            # Convert back to style string
            return f"{modified_style['tone']}_{modified_style['pitch']}"
            
        except Exception as e:
            logger.error(f"Error applying voice style: {e}")
            return voice_style
    
    async def generate_gesture_timeline(
        self, 
        text: str, 
        gesture_tag: GestureTag,
        emotion: Emotion
    ) -> List[Dict[str, Any]]:
        """Generate timeline of gestures synchronized with text"""
        try:
            timeline = []
            words = text.split()
            word_duration = 0.5  # seconds per word (estimated)
            
            # Get emotion intensity
            emotion_config = self.emotion_modifiers.get(emotion, self.emotion_modifiers[Emotion.NEUTRAL])
            intensity = emotion_config['gesture_intensity']
            
            # Map intensity to gesture parameters
            intensity_params = {
                'low': {'frequency': 0.3, 'duration': 0.5},
                'medium': {'frequency': 0.5, 'duration': 0.8},
                'high': {'frequency': 0.8, 'duration': 1.2}
            }
            
            params = intensity_params.get(intensity, intensity_params['medium'])
            
            # Generate gestures at intervals
            gesture_interval = int(1 / params['frequency'])  # words between gestures
            current_time = 0
            
            for i, word in enumerate(words):
                if i % gesture_interval == 0:
                    gesture = {
                        'time': current_time,
                        'duration': params['duration'],
                        'type': gesture_tag.value,
                        'intensity': intensity,
                        'word': word
                    }
                    timeline.append(gesture)
                
                current_time += word_duration
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error generating gesture timeline: {e}")
            return []
    
    async def get_voice_style_info(self, voice_style: str) -> Dict[str, Any]:
        """Get information about a voice style"""
        return self.voice_styles.get(voice_style, self.voice_styles['friendly_male'])
    
    async def get_emotion_info(self, emotion: Emotion) -> Dict[str, Any]:
        """Get information about an emotion configuration"""
        return self.emotion_modifiers.get(emotion, self.emotion_modifiers[Emotion.NEUTRAL])
    
    async def add_custom_gesture_mapping(
        self, 
        gesture: GestureTag, 
        triggers: List[str]
    ) -> bool:
        """Add custom gesture trigger words"""
        try:
            if gesture not in self.gesture_mapping:
                self.gesture_mapping[gesture] = {
                    'triggers': [],
                    'gesture': gesture.value,
                    'frequency': 'medium'
                }
            
            self.gesture_mapping[gesture]['triggers'].extend(triggers)
            logger.info(f"Added custom gesture mapping for {gesture}: {triggers}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom gesture mapping: {e}")
            return False
    
    async def optimize_for_avatar(
        self, 
        response: ResponseSynthesizerOutput,
        avatar_capabilities: Dict[str, Any]
    ) -> ResponseSynthesizerOutput:
        """Optimize response for specific avatar capabilities"""
        try:
            # Check if avatar supports specific gestures
            supported_gestures = avatar_capabilities.get('gestures', [])
            if response.gesture_tag.value not in supported_gestures:
                # Fall back to a supported gesture
                fallback_gesture = supported_gestures[0] if supported_gestures else GestureTag.AFFIRMATIVE
                response.gesture_tag = fallback_gesture
            
            # Check if avatar supports emphasis
            if not avatar_capabilities.get('emphasis', False):
                response.emphasis_spans = []
            
            # Adjust for avatar language support
            supported_languages = avatar_capabilities.get('languages', [])
            if response.language not in supported_languages:
                # Use fallback language
                response.language = supported_languages[0] if supported_languages else 'en'
            
            logger.info(f"Optimized response for avatar capabilities")
            return response
            
        except Exception as e:
            logger.error(f"Error optimizing for avatar: {e}")
            return response