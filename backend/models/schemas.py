from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    GUJARATI = "gu"
    SPANISH = "es"
    FRENCH = "fr"

class Persona(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    ENCOURAGING = "encouraging"
    STRICT = "strict"

class Subject(str, Enum):
    MATH = "math"
    SCIENCE = "science"
    PROGRAMMING = "programming"
    GENERAL = "general"
    HISTORY = "history"
    LITERATURE = "literature"

class Intent(str, Enum):
    ASK = "ask"
    CHECK_HOMEWORK = "check-homework"
    START_QUIZ = "start-quiz"
    SMALL_TALK = "small-talk"
    ESCALATE = "escalate"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Emotion(str, Enum):
    CALM = "calm"
    ENCOURAGING = "encouraging"
    CORRECTIVE = "corrective"
    EXCITED = "excited"
    NEUTRAL = "neutral"

class GestureTag(str, Enum):
    AFFIRMATIVE = "affirmative"
    CORRECTIVE = "corrective"
    ILLUSTRATIVE = "illustrative"
    QUESTIONING = "questioning"
    POINTING = "pointing"

# Session Management
class SessionCreate(BaseModel):
    user_id: str
    language: Language = Language.ENGLISH
    persona: Persona = Persona.FRIENDLY

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    language: Language
    persona: Persona
    created_at: datetime
    context_window: List[Dict[str, Any]] = []

# Audio Processing
class AudioRequest(BaseModel):
    session_id: str
    language_hint: Optional[Language] = None

class AudioResponse(BaseModel):
    transcript: str
    language: Language
    confidence: float
    timings: Optional[List[Dict[str, float]]] = None

# Text Processing
class TextRequest(BaseModel):
    text: str
    session_id: str
    language: Optional[Language] = None

class TextResponse(BaseModel):
    text: str
    summary: Optional[str] = None
    confidence: float
    need_steps: bool = False
    citations: List[str] = []
    voice_style: str = "friendly_male"
    emotion: Emotion = Emotion.NEUTRAL
    gesture_tag: GestureTag = GestureTag.AFFIRMATIVE
    emphasis_spans: List[Dict[str, int]] = []

# Quiz System
class QuizRequest(BaseModel):
    topic: str
    difficulty: Difficulty
    subject: Subject
    session_id: str
    num_questions: int = 5

class QuizQuestion(BaseModel):
    question_id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None
    hint: Optional[str] = None

class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[QuizQuestion]
    time_limit: Optional[int] = None
    instructions: str

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[int]
    session_id: str

class QuizResult(BaseModel):
    score: float
    total_questions: int
    correct_answers: int
    detailed_feedback: List[Dict[str, Any]]
    remediation_plan: List[str]

# Homework Checking
class HomeworkRequest(BaseModel):
    session_id: str
    subject: Subject
    expected_format: Optional[str] = None

class HomeworkResponse(BaseModel):
    verdict: str  # correct/incorrect/partial
    score: float
    short_reason: str
    detailed_explanation: Optional[str] = None
    suggestions: List[str] = []
    confidence: float

# Agent Communication
class AgentRequest(BaseModel):
    session_id: str
    user_id: str
    text: str
    language: str
    subject: Subject
    context: List[Dict[str, Any]] = []

class TeachingAgentResponse(BaseModel):
    text: str
    summary: Optional[str] = None
    confidence: float
    need_steps: bool = False
    citations: List[str] = []

class ResponseSynthesizerInput(BaseModel):
    text: str
    voice_style: str = "friendly_male"
    language: str = "en"
    emotion: Emotion = Emotion.NEUTRAL
    gesture_tag: GestureTag = GestureTag.AFFIRMATIVE
    priority: str = "interactive"
    avatar_template: str = "teacher_1"

class ResponseSynthesizerOutput(BaseModel):
    text: str
    voice_style: str
    language: str
    emotion: Emotion
    gesture_tag: GestureTag
    emphasis_spans: List[Dict[str, int]] = []

class TTSOutput(BaseModel):
    audio_url: Optional[str] = None
    audio_data: Optional[bytes] = None
    phoneme_timestamps: List[Dict[str, Union[str, float]]] = []

class AvatarCoordinatorOutput(BaseModel):
    video_url: Optional[str] = None
    webrtc_token: Optional[str] = None
    expected_delay_ms: int = 1500
    gesture_timeline: List[Dict[str, Any]] = []

# Memory and Context
class MemoryEntry(BaseModel):
    timestamp: datetime
    type: str  # question, answer, feedback, etc.
    content: str
    metadata: Dict[str, Any] = {}

class ContextWindow(BaseModel):
    session_id: str
    entries: List[MemoryEntry]
    max_size: int = 10

# Error Handling
class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: datetime
    session_id: Optional[str] = None

# WebSocket Messages
class WebSocketMessage(BaseModel):
    type: str  # audio, text, response, error
    data: Any
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

class AudioChunk(BaseModel):
    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"

class StreamingResponse(BaseModel):
    type: str  # partial, final
    content: str
    metadata: Dict[str, Any] = {}
    is_final: bool = False