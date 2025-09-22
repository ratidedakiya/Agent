# AI Tutor Application API Documentation

## Overview

The AI Tutor Application provides a comprehensive REST API and WebSocket interface for multi-agent AI tutoring with voice interaction, avatar support, and intelligent content generation.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

Currently, the API uses session-based authentication. Each request should include the session ID in the request body or as a query parameter.

## Content Types

- **JSON**: `application/json`
- **Multipart**: `multipart/form-data` (for file uploads)
- **WebSocket**: `text/plain` (for real-time communication)

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "timestamp": "2024-01-01T00:00:00Z",
  "session_id": "optional-session-id"
}
```

## Endpoints

### Session Management

#### Create Session
```http
POST /api/sessions
Content-Type: application/json

{
  "user_id": "string",
  "language": "en|hi|gu|es|fr",
  "persona": "friendly|professional|encouraging|strict"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user_id": "string",
  "language": "en",
  "persona": "friendly",
  "created_at": "2024-01-01T00:00:00Z",
  "context_window": []
}
```

#### Get Session
```http
GET /api/sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user_id": "string",
  "language": "en",
  "persona": "friendly",
  "created_at": "2024-01-01T00:00:00Z",
  "context_window": []
}
```

### Audio Processing

#### Transcribe Audio
```http
POST /api/audio/transcribe
Content-Type: multipart/form-data

audio_file: [binary file]
session_id: string (optional)
```

**Response:**
```json
{
  "transcript": "string",
  "language": "en",
  "confidence": 0.95,
  "timings": [
    {
      "word": "hello",
      "start": 0.0,
      "end": 0.5,
      "duration": 0.5
    }
  ]
}
```

#### Stream Audio
```http
POST /api/audio/stream
Content-Type: multipart/form-data

audio_file: [binary file]
session_id: string (optional)
```

**Response:** Server-Sent Events stream with partial results.

### Text Processing

#### Process Text
```http
POST /api/text/process
Content-Type: application/json

{
  "text": "string",
  "session_id": "uuid",
  "language": "en" (optional)
}
```

**Response:**
```json
{
  "text": "AI response text",
  "summary": "Brief summary",
  "confidence": 0.95,
  "need_steps": true,
  "citations": ["source1", "source2"],
  "voice_style": "friendly_male",
  "emotion": "encouraging",
  "gesture_tag": "affirmative",
  "emphasis_spans": [
    {
      "start": 0,
      "end": 10,
      "content": "important",
      "type": "bold"
    }
  ]
}
```

### Quiz System

#### Generate Quiz
```http
POST /api/quiz/generate
Content-Type: application/json

{
  "topic": "string",
  "difficulty": "easy|medium|hard",
  "subject": "math|science|programming|history|literature|general",
  "session_id": "uuid",
  "num_questions": 5 (optional)
}
```

**Response:**
```json
{
  "quiz_id": "uuid",
  "questions": [
    {
      "question_id": "uuid",
      "question": "What is 2+2?",
      "options": ["3", "4", "5", "6"],
      "correct_answer": 1,
      "explanation": "2+2 equals 4",
      "hint": "Add the numbers together"
    }
  ],
  "time_limit": 300,
  "instructions": "Answer all questions"
}
```

#### Submit Quiz
```http
POST /api/quiz/submit
Content-Type: application/json

{
  "quiz_id": "uuid",
  "answers": [1, 2, 0, 3, 1],
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "score": 85.0,
  "total_questions": 5,
  "correct_answers": 4,
  "detailed_feedback": [
    {
      "question_id": "uuid",
      "correct": true,
      "user_answer": 1,
      "correct_answer": 1,
      "explanation": "Correct!"
    }
  ],
  "remediation_plan": ["Review algebra basics", "Practice more problems"]
}
```

### Homework Checking

#### Check Homework
```http
POST /api/homework/check
Content-Type: multipart/form-data

homework_file: [binary file]
session_id: string (optional)
subject: string (optional)
```

**Response:**
```json
{
  "verdict": "correct|incorrect|partial",
  "score": 85.0,
  "short_reason": "Good work overall with minor errors",
  "detailed_explanation": "Your solution shows good understanding...",
  "suggestions": ["Check calculations", "Review formulas"],
  "confidence": 0.8
}
```

### WebSocket Communication

#### Connect to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{session_id}');
```

#### Send Message
```json
{
  "type": "audio|text|response|error",
  "data": "message content or binary data",
  "session_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Receive Message
```json
{
  "type": "partial|final|error",
  "content": "response content",
  "metadata": {
    "confidence": 0.95,
    "emotion": "encouraging",
    "gesture_tag": "affirmative"
  },
  "is_final": false
}
```

## Data Models

### Language Enum
```typescript
enum Language {
  ENGLISH = "en",
  HINDI = "hi",
  GUJARATI = "gu",
  SPANISH = "es",
  FRENCH = "fr"
}
```

### Persona Enum
```typescript
enum Persona {
  FRIENDLY = "friendly",
  PROFESSIONAL = "professional",
  ENCOURAGING = "encouraging",
  STRICT = "strict"
}
```

### Subject Enum
```typescript
enum Subject {
  MATH = "math",
  SCIENCE = "science",
  PROGRAMMING = "programming",
  HISTORY = "history",
  LITERATURE = "literature",
  GENERAL = "general"
}
```

### Intent Enum
```typescript
enum Intent {
  ASK = "ask",
  CHECK_HOMEWORK = "check-homework",
  START_QUIZ = "start-quiz",
  SMALL_TALK = "small-talk",
  ESCALATE = "escalate"
}
```

### Emotion Enum
```typescript
enum Emotion {
  CALM = "calm",
  ENCOURAGING = "encouraging",
  CORRECTIVE = "corrective",
  EXCITED = "excited",
  NEUTRAL = "neutral"
}
```

### GestureTag Enum
```typescript
enum GestureTag {
  AFFIRMATIVE = "affirmative",
  CORRECTIVE = "corrective",
  ILLUSTRATIVE = "illustrative",
  QUESTIONING = "questioning",
  POINTING = "pointing"
}
```

## Rate Limiting

- **Text Processing**: 60 requests per minute per session
- **Audio Processing**: 30 requests per minute per session
- **Quiz Generation**: 10 requests per minute per session
- **Homework Checking**: 5 requests per minute per session

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing session |
| 403 | Forbidden - Rate limit exceeded |
| 404 | Not Found - Resource not found |
| 413 | Payload Too Large - File size exceeds limit |
| 415 | Unsupported Media Type - Invalid file format |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

## WebSocket Events

### Client Events

#### Audio Chunk
```json
{
  "type": "audio",
  "data": "base64_encoded_audio_chunk",
  "session_id": "uuid"
}
```

#### Text Message
```json
{
  "type": "text",
  "data": "Hello, can you help me with math?",
  "session_id": "uuid"
}
```

### Server Events

#### Partial Response
```json
{
  "type": "partial",
  "content": "Let me help you with that math problem...",
  "metadata": {
    "confidence": 0.8,
    "is_final": false
  }
}
```

#### Final Response
```json
{
  "type": "final",
  "content": "Here's the complete solution to your math problem...",
  "metadata": {
    "confidence": 0.95,
    "emotion": "encouraging",
    "gesture_tag": "illustrative",
    "voice_style": "friendly_male",
    "audio_data": "base64_encoded_audio",
    "video_url": "https://example.com/avatar.mp4"
  },
  "is_final": true
}
```

#### Error Event
```json
{
  "type": "error",
  "content": "Sorry, I encountered an error processing your request.",
  "error": "Processing failed",
  "is_final": true
}
```

## Examples

### Complete Chat Flow

1. **Create Session**
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "language": "en", "persona": "friendly"}'
```

2. **Send Text Message**
```bash
curl -X POST http://localhost:8000/api/text/process \
  -H "Content-Type: application/json" \
  -d '{"text": "What is photosynthesis?", "session_id": "session-uuid"}'
```

3. **Upload Audio**
```bash
curl -X POST http://localhost:8000/api/audio/transcribe \
  -F "audio_file=@recording.wav" \
  -F "session_id=session-uuid"
```

### WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session-uuid');

ws.onopen = () => {
  console.log('Connected to AI Tutor');
  
  // Send text message
  ws.send(JSON.stringify({
    type: 'text',
    data: 'Hello, can you help me with algebra?',
    session_id: 'session-uuid'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  if (data.is_final) {
    // Handle final response
    displayResponse(data.content);
    if (data.metadata.audio_data) {
      playAudio(data.metadata.audio_data);
    }
  }
};
```

## SDK Examples

### Python SDK
```python
import requests
import json

class AITutorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
    
    def create_session(self, user_id, language="en", persona="friendly"):
        response = requests.post(f"{self.base_url}/api/sessions", json={
            "user_id": user_id,
            "language": language,
            "persona": persona
        })
        data = response.json()
        self.session_id = data["session_id"]
        return data
    
    def send_message(self, text):
        response = requests.post(f"{self.base_url}/api/text/process", json={
            "text": text,
            "session_id": self.session_id
        })
        return response.json()

# Usage
client = AITutorClient()
client.create_session("user123")
response = client.send_message("What is 2+2?")
print(response["text"])
```

### JavaScript SDK
```javascript
class AITutorClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }
  
  async createSession(userId, language = 'en', persona = 'friendly') {
    const response = await fetch(`${this.baseUrl}/api/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, language, persona })
    });
    const data = await response.json();
    this.sessionId = data.session_id;
    return data;
  }
  
  async sendMessage(text) {
    const response = await fetch(`${this.baseUrl}/api/text/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, session_id: this.sessionId })
    });
    return response.json();
  }
}

// Usage
const client = new AITutorClient();
await client.createSession('user123');
const response = await client.sendMessage('What is 2+2?');
console.log(response.text);
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## Support

For API support and questions:
- Check the interactive documentation at `/docs`
- Review the error responses for troubleshooting
- Check the server logs for detailed error information