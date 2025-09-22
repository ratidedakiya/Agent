import io
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine
import requests
import json
from models.schemas import Language, Emotion, TTSOutput

logger = logging.getLogger(__name__)

class TTSAgent:
    """Text-to-Speech agent with multiple voice options and emotion support"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        
        # Voice configurations for different languages and emotions
        self.voice_configs = {
            Language.ENGLISH: {
                'voices': {
                    'friendly_male': 'alloy',
                    'friendly_female': 'nova',
                    'professional_male': 'onyx',
                    'professional_female': 'shimmer',
                    'encouraging_male': 'echo',
                    'encouraging_female': 'fable'
                },
                'default_voice': 'alloy'
            },
            Language.HINDI: {
                'voices': {
                    'friendly_male': 'alloy',  # Fallback to English voices
                    'friendly_female': 'nova',
                    'professional_male': 'onyx',
                    'professional_female': 'shimmer'
                },
                'default_voice': 'alloy'
            },
            Language.GUJARATI: {
                'voices': {
                    'friendly_male': 'alloy',
                    'friendly_female': 'nova',
                    'professional_male': 'onyx',
                    'professional_female': 'shimmer'
                },
                'default_voice': 'alloy'
            },
            Language.SPANISH: {
                'voices': {
                    'friendly_male': 'alloy',
                    'friendly_female': 'nova',
                    'professional_male': 'onyx',
                    'professional_female': 'shimmer'
                },
                'default_voice': 'alloy'
            },
            Language.FRENCH: {
                'voices': {
                    'friendly_male': 'alloy',
                    'friendly_female': 'nova',
                    'professional_male': 'onyx',
                    'professional_female': 'shimmer'
                },
                'default_voice': 'alloy'
            }
        }
        
        # Emotion-based voice modifications
        self.emotion_modifications = {
            Emotion.CALM: {
                'speed': 0.9,
                'pitch_shift': -0.1,
                'volume_adjustment': -0.1
            },
            Emotion.ENCOURAGING: {
                'speed': 1.1,
                'pitch_shift': 0.1,
                'volume_adjustment': 0.1
            },
            Emotion.CORRECTIVE: {
                'speed': 0.8,
                'pitch_shift': -0.05,
                'volume_adjustment': 0.0
            },
            Emotion.EXCITED: {
                'speed': 1.2,
                'pitch_shift': 0.2,
                'volume_adjustment': 0.2
            },
            Emotion.NEUTRAL: {
                'speed': 1.0,
                'pitch_shift': 0.0,
                'volume_adjustment': 0.0
            }
        }
    
    async def synthesize_speech(
        self,
        text: str,
        voice_style: str = "friendly_male",
        language: Language = Language.ENGLISH,
        emotion: Emotion = Emotion.NEUTRAL
    ) -> TTSOutput:
        """Synthesize speech from text with specified voice and emotion"""
        try:
            # Get voice configuration
            voice_config = self.voice_configs.get(language, self.voice_configs[Language.ENGLISH])
            voice_name = voice_config['voices'].get(voice_style, voice_config['default_voice'])
            
            # Generate audio using OpenAI TTS
            if self.openai_api_key:
                audio_data = await self._generate_with_openai(text, voice_name)
            else:
                # Fallback to basic synthesis
                audio_data = await self._generate_basic_speech(text, voice_style, emotion)
            
            # Apply emotion modifications
            modified_audio = await self._apply_emotion_modifications(audio_data, emotion)
            
            # Generate phoneme timestamps
            phoneme_timestamps = await self._generate_phoneme_timestamps(text, modified_audio)
            
            logger.info(f"Generated TTS audio for {len(text)} characters with {voice_style} voice")
            
            return TTSOutput(
                audio_data=modified_audio,
                phoneme_timestamps=phoneme_timestamps
            )
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return TTSOutput(
                audio_data=b'',
                phoneme_timestamps=[]
            )
    
    async def _generate_with_openai(self, text: str, voice_name: str) -> bytes:
        """Generate speech using OpenAI TTS API"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice_name,
                input=text
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error with OpenAI TTS: {e}")
            raise
    
    async def _generate_basic_speech(
        self, 
        text: str, 
        voice_style: str, 
        emotion: Emotion
    ) -> bytes:
        """Generate basic speech as fallback"""
        try:
            # Simple text-to-speech using pydub
            # This is a basic implementation - in production, use a proper TTS service
            
            # Create a simple tone sequence based on text
            words = text.split()
            audio_segments = []
            
            for word in words:
                # Generate a tone for each word (simplified)
                duration = len(word) * 100  # ms per character
                frequency = 440 + (hash(word) % 200)  # Vary frequency based on word
                
                tone = Sine(frequency).to_audio_segment(duration=duration)
                audio_segments.append(tone)
                
                # Add small pause between words
                pause = AudioSegment.silent(duration=50)
                audio_segments.append(pause)
            
            # Combine all segments
            if audio_segments:
                combined = sum(audio_segments)
            else:
                combined = AudioSegment.silent(duration=1000)
            
            # Convert to bytes
            wav_io = io.BytesIO()
            combined.export(wav_io, format="wav")
            return wav_io.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating basic speech: {e}")
            return b''
    
    async def _apply_emotion_modifications(
        self, 
        audio_data: bytes, 
        emotion: Emotion
    ) -> bytes:
        """Apply emotion-based modifications to audio"""
        try:
            if not audio_data:
                return audio_data
            
            # Load audio
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Get emotion modifications
            modifications = self.emotion_modifications.get(emotion, self.emotion_modifications[Emotion.NEUTRAL])
            
            # Apply speed modification
            if modifications['speed'] != 1.0:
                audio = audio.speedup(playback_speed=modifications['speed'])
            
            # Apply pitch shift
            if modifications['pitch_shift'] != 0:
                # Simple pitch shift using speed change
                pitch_factor = 2 ** modifications['pitch_shift']
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * pitch_factor)})
                audio = audio.set_frame_rate(audio.frame_rate)
            
            # Apply volume adjustment
            if modifications['volume_adjustment'] != 0:
                volume_db = modifications['volume_adjustment'] * 20  # Convert to dB
                audio = audio + volume_db
            
            # Export modified audio
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            return wav_io.getvalue()
            
        except Exception as e:
            logger.error(f"Error applying emotion modifications: {e}")
            return audio_data
    
    async def _generate_phoneme_timestamps(
        self, 
        text: str, 
        audio_data: bytes
    ) -> List[Dict[str, Any]]:
        """Generate phoneme timestamps for lip-sync"""
        try:
            if not audio_data:
                return []
            
            # Load audio to get duration
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            duration_ms = len(audio)
            
            # Simple phoneme timing estimation
            words = text.split()
            phoneme_timestamps = []
            
            if not words:
                return []
            
            # Estimate timing per word
            time_per_word = duration_ms / len(words)
            current_time = 0
            
            for word in words:
                # Simple phoneme breakdown (vowels and consonants)
                phonemes = self._break_into_phonemes(word)
                word_duration = time_per_word
                phoneme_duration = word_duration / len(phonemes) if phonemes else word_duration
                
                for phoneme in phonemes:
                    phoneme_timestamps.append({
                        'phoneme': phoneme,
                        'start': current_time / 1000,  # Convert to seconds
                        'end': (current_time + phoneme_duration) / 1000,
                        'duration': phoneme_duration / 1000
                    })
                    current_time += phoneme_duration
                
                # Add small pause between words
                current_time += 50  # 50ms pause
            
            return phoneme_timestamps
            
        except Exception as e:
            logger.error(f"Error generating phoneme timestamps: {e}")
            return []
    
    def _break_into_phonemes(self, word: str) -> List[str]:
        """Break word into basic phonemes for timing"""
        # Simplified phoneme breakdown
        # In production, use a proper phoneme analysis library
        
        phonemes = []
        vowels = 'aeiouAEIOU'
        consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        
        i = 0
        while i < len(word):
            char = word[i]
            
            if char in vowels:
                phonemes.append(char.lower())
            elif char in consonants:
                phonemes.append(char.lower())
            else:
                # Skip non-alphabetic characters
                pass
            
            i += 1
        
        return phonemes if phonemes else ['a']  # Fallback to single phoneme
    
    async def get_available_voices(self, language: Language) -> List[str]:
        """Get list of available voices for a language"""
        voice_config = self.voice_configs.get(language, self.voice_configs[Language.ENGLISH])
        return list(voice_config['voices'].keys())
    
    async def get_voice_info(self, voice_style: str, language: Language) -> Dict[str, Any]:
        """Get information about a specific voice"""
        voice_config = self.voice_configs.get(language, self.voice_configs[Language.ENGLISH])
        voice_name = voice_config['voices'].get(voice_style, voice_config['default_voice'])
        
        return {
            'voice_style': voice_style,
            'voice_name': voice_name,
            'language': language.value,
            'available': voice_style in voice_config['voices']
        }
    
    async def test_voice(self, voice_style: str, language: Language) -> bool:
        """Test if a voice is working properly"""
        try:
            test_text = "Hello, this is a test."
            result = await self.synthesize_speech(
                text=test_text,
                voice_style=voice_style,
                language=language
            )
            
            return len(result.audio_data) > 0
            
        except Exception as e:
            logger.error(f"Error testing voice {voice_style}: {e}")
            return False
    
    async def get_emotion_modifications(self, emotion: Emotion) -> Dict[str, float]:
        """Get emotion modification parameters"""
        return self.emotion_modifications.get(emotion, self.emotion_modifications[Emotion.NEUTRAL])
    
    async def set_voice_config(
        self, 
        language: Language, 
        voice_style: str, 
        voice_name: str
    ) -> bool:
        """Set custom voice configuration"""
        try:
            if language not in self.voice_configs:
                self.voice_configs[language] = {
                    'voices': {},
                    'default_voice': voice_name
                }
            
            self.voice_configs[language]['voices'][voice_style] = voice_name
            logger.info(f"Set voice config: {language} - {voice_style} -> {voice_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting voice config: {e}")
            return False
    
    async def get_audio_duration(self, audio_data: bytes) -> float:
        """Get duration of audio data in seconds"""
        try:
            if not audio_data:
                return 0.0
            
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            return len(audio) / 1000.0  # Convert ms to seconds
            
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    async def normalize_audio(self, audio_data: bytes) -> bytes:
        """Normalize audio volume and quality"""
        try:
            if not audio_data:
                return audio_data
            
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
            
            # Normalize volume
            audio = audio.normalize()
            
            # Apply basic noise reduction
            audio = audio.high_pass_filter(80)
            audio = audio.low_pass_filter(8000)
            
            # Export normalized audio
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            return wav_io.getvalue()
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio_data