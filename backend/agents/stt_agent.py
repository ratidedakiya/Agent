import io
import wave
import logging
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import numpy as np
from pydub import AudioSegment
import speech_recognition as sr
import webrtcvad
from models.schemas import Language, AudioResponse

logger = logging.getLogger(__name__)

class STTAgent:
    """Speech-to-Text agent with streaming support and multiple language support"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # Language-specific configurations
        self.language_configs = {
            Language.ENGLISH: {
                "google_lang": "en-US",
                "confidence_threshold": 0.7,
                "vad_aggressiveness": 2
            },
            Language.HINDI: {
                "google_lang": "hi-IN",
                "confidence_threshold": 0.6,
                "vad_aggressiveness": 1
            },
            Language.GUJARATI: {
                "google_lang": "gu-IN",
                "confidence_threshold": 0.6,
                "vad_aggressiveness": 1
            },
            Language.SPANISH: {
                "google_lang": "es-ES",
                "confidence_threshold": 0.7,
                "vad_aggressiveness": 2
            },
            Language.FRENCH: {
                "google_lang": "fr-FR",
                "confidence_threshold": 0.7,
                "vad_aggressiveness": 2
            }
        }
    
    async def transcribe_audio(
        self, 
        audio_data: bytes, 
        language: Language = Language.ENGLISH,
        language_hint: Optional[Language] = None
    ) -> AudioResponse:
        """Convert audio to text with confidence and timing information"""
        try:
            # Use language hint if provided
            target_language = language_hint or language
            config = self.language_configs.get(target_language, self.language_configs[Language.ENGLISH])
            
            # Convert audio data to AudioSegment
            audio_segment = self._bytes_to_audio_segment(audio_data)
            
            # Preprocess audio
            processed_audio = self._preprocess_audio(audio_segment)
            
            # Convert to format expected by speech_recognition
            wav_data = self._audio_segment_to_wav_bytes(processed_audio)
            
            # Create AudioData object
            audio_data_obj = sr.AudioData(
                wav_data, 
                self.sample_rate, 
                2  # 16-bit samples
            )
            
            # Perform speech recognition
            try:
                transcript = self.recognizer.recognize_google(
                    audio_data_obj,
                    language=config["google_lang"],
                    show_all=True
                )
                
                if isinstance(transcript, dict) and 'alternative' in transcript:
                    # Get the best result
                    best_result = transcript['alternative'][0]
                    text = best_result.get('transcript', '')
                    confidence = best_result.get('confidence', 0.0)
                else:
                    text = str(transcript) if transcript else ''
                    confidence = 0.8  # Default confidence
                
                # Check confidence threshold
                if confidence < config["confidence_threshold"]:
                    logger.warning(f"Low confidence transcription: {confidence}")
                
                # Generate timing information
                timings = await self._generate_timings(processed_audio, text)
                
                # Detect actual language if different from expected
                detected_language = await self._detect_language(text, target_language)
                
                logger.info(f"Transcribed audio: '{text[:50]}...' (confidence: {confidence:.2f})")
                
                return AudioResponse(
                    transcript=text,
                    language=detected_language,
                    confidence=confidence,
                    timings=timings
                )
                
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return AudioResponse(
                    transcript="",
                    language=target_language,
                    confidence=0.0,
                    timings=[]
                )
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                raise Exception(f"Speech recognition failed: {e}")
                
        except Exception as e:
            logger.error(f"Error in STT transcription: {e}")
            raise
    
    async def transcribe_streaming(
        self, 
        audio_chunks: List[bytes], 
        language: Language = Language.ENGLISH
    ) -> AudioResponse:
        """Transcribe streaming audio chunks"""
        try:
            # Combine audio chunks
            combined_audio = b''.join(audio_chunks)
            
            # Use regular transcription
            return await self.transcribe_audio(combined_audio, language)
            
        except Exception as e:
            logger.error(f"Error in streaming STT: {e}")
            raise
    
    async def detect_voice_activity(self, audio_chunk: bytes) -> bool:
        """Detect if audio chunk contains voice activity"""
        try:
            # Convert to numpy array
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Ensure correct frame size
            if len(audio_array) != self.frame_size:
                # Resize if necessary
                if len(audio_array) > self.frame_size:
                    audio_array = audio_array[:self.frame_size]
                else:
                    # Pad with zeros
                    audio_array = np.pad(audio_array, (0, self.frame_size - len(audio_array)))
            
            # Convert to bytes
            audio_bytes = audio_array.tobytes()
            
            # Use VAD to detect voice activity
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
            
            return is_speech
            
        except Exception as e:
            logger.error(f"Error detecting voice activity: {e}")
            return False
    
    def _bytes_to_audio_segment(self, audio_data: bytes) -> AudioSegment:
        """Convert raw bytes to AudioSegment"""
        try:
            # Try to detect format and load
            audio_io = io.BytesIO(audio_data)
            
            # Try different formats
            for format_type in ['wav', 'mp3', 'ogg', 'm4a']:
                try:
                    audio_io.seek(0)
                    audio = AudioSegment.from_file(audio_io, format=format_type)
                    return audio
                except:
                    continue
            
            # If no format works, assume raw WAV
            audio_io.seek(0)
            return AudioSegment.from_wav(audio_io)
            
        except Exception as e:
            logger.error(f"Error converting bytes to audio segment: {e}")
            # Return empty audio segment as fallback
            return AudioSegment.silent(duration=1000)
    
    def _audio_segment_to_wav_bytes(self, audio_segment: AudioSegment) -> bytes:
        """Convert AudioSegment to WAV bytes"""
        try:
            # Ensure correct sample rate and channels
            audio = audio_segment.set_frame_rate(self.sample_rate).set_channels(1)
            
            # Convert to WAV bytes
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            
            return wav_io.read()
            
        except Exception as e:
            logger.error(f"Error converting audio segment to WAV: {e}")
            return b''
    
    def _preprocess_audio(self, audio_segment: AudioSegment) -> AudioSegment:
        """Preprocess audio for better recognition"""
        try:
            # Normalize volume
            audio = audio_segment.normalize()
            
            # Apply noise reduction (simple high-pass filter)
            audio = audio.high_pass_filter(80)
            
            # Apply low-pass filter
            audio = audio.low_pass_filter(8000)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            return audio_segment
    
    async def _generate_timings(
        self, 
        audio_segment: AudioSegment, 
        text: str
    ) -> List[Dict[str, float]]:
        """Generate timing information for words/phrases"""
        try:
            # Simple timing estimation based on audio duration and text length
            duration_ms = len(audio_segment)
            words = text.split()
            
            if not words:
                return []
            
            # Estimate timing per word
            time_per_word = duration_ms / len(words)
            
            timings = []
            current_time = 0
            
            for word in words:
                word_duration = time_per_word * (len(word) / 10)  # Adjust for word length
                timings.append({
                    "word": word,
                    "start": current_time / 1000,  # Convert to seconds
                    "end": (current_time + word_duration) / 1000,
                    "duration": word_duration / 1000
                })
                current_time += word_duration
            
            return timings
            
        except Exception as e:
            logger.error(f"Error generating timings: {e}")
            return []
    
    async def _detect_language(
        self, 
        text: str, 
        expected_language: Language
    ) -> Language:
        """Detect the actual language of transcribed text"""
        try:
            if not text.strip():
                return expected_language
            
            # Simple language detection based on character patterns
            # This is a basic implementation - in production, use a proper language detection library
            
            # Check for Devanagari script (Hindi)
            if any('\u0900' <= char <= '\u097F' for char in text):
                return Language.HINDI
            
            # Check for Gujarati script
            if any('\u0A80' <= char <= '\u0AFF' for char in text):
                return Language.GUJARATI
            
            # Check for Spanish characters
            spanish_chars = ['ñ', 'á', 'é', 'í', 'ó', 'ú', 'ü']
            if any(char in text.lower() for char in spanish_chars):
                return Language.SPANISH
            
            # Check for French characters
            french_chars = ['à', 'â', 'ä', 'ç', 'é', 'è', 'ê', 'ë', 'î', 'ï', 'ô', 'ö', 'ù', 'û', 'ü', 'ÿ']
            if any(char in text.lower() for char in french_chars):
                return Language.FRENCH
            
            # Default to expected language
            return expected_language
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return expected_language
    
    async def get_supported_languages(self) -> List[Language]:
        """Get list of supported languages"""
        return list(self.language_configs.keys())
    
    async def get_language_config(self, language: Language) -> Dict[str, Any]:
        """Get configuration for a specific language"""
        return self.language_configs.get(language, self.language_configs[Language.ENGLISH])