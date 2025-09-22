
# AI Integration Tutor Application

A comprehensive multi-agent AI tutoring system with voice interaction, avatar support, and intelligent content generation. Built with FastAPI backend, React frontend, and LangChain/LangGraph for AI orchestration.

## 🚀 Features

### Core Capabilities
- **Multi-Agent Architecture**: Coordinated AI agents for different tasks
- **Voice Interaction**: Speech-to-text and text-to-speech with emotion support
- **Avatar Integration**: Animated AI tutor with gesture and emotion synchronization
- **Multi-Language Support**: English, Hindi, Gujarati, Spanish, French
- **Real-time Communication**: WebSocket support for live interaction

### Learning Features
- **Intelligent Q&A**: Context-aware responses with step-by-step explanations
- **Quiz Generation**: AI-powered quizzes with multiple difficulty levels
- **Homework Review**: OCR-based homework checking with detailed feedback
- **Progress Tracking**: Session management and learning analytics
- **Personalized Learning**: Adaptive responses based on user preferences

### Technical Features
- **Streaming Audio**: Real-time audio processing and playback
- **Gesture Recognition**: Avatar gestures synchronized with speech
- **Error Handling**: Robust fallback mechanisms and error recovery
- **Rate Limiting**: Built-in protection against abuse
- **Caching**: Redis-based caching for improved performance

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── agents/                 # AI Agent implementations
│   ├── session_manager.py  # Session and context management
│   ├── stt_agent.py       # Speech-to-text processing
│   ├── language_detector.py # Language detection and normalization
│   ├── intent_router.py   # Intent classification and routing
│   ├── teaching_agent.py  # Core teaching logic with LangChain
│   ├── response_synthesizer.py # Response formatting and metadata
│   ├── tts_agent.py       # Text-to-speech generation
│   ├── avatar_coordinator.py # Avatar video generation
│   └── orchestrator.py    # LangGraph-based agent coordination
├── models/                # Data models and schemas
├── database/              # Database connection and models
├── utils/                 # Configuration and utilities
└── main.py               # FastAPI application entry point
```

### Frontend (React)
```
src/
├── components/            # React components
│   ├── ChatInterface.js   # Main chat interface
│   ├── QuizInterface.js   # Quiz generation and taking
│   ├── HomeworkInterface.js # Homework upload and review
│   ├── Settings.js        # User preferences
│   ├── AudioRecorder.js   # Voice recording component
│   ├── MessageBubble.js   # Chat message display
│   └── AvatarVideo.js     # Avatar video player
├── context/               # React context providers
├── App.js                # Main application component
└── index.js              # Application entry point
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis (for caching)
- FFmpeg (for audio processing)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-tutor-application
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from backend.database.connection import create_tables; create_tables()"
   ```

6. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///./ai_tutor.db

# Redis
REDIS_URL=redis://localhost:6379

# Features
ENABLE_AVATAR=true
ENABLE_STREAMING=true
ENABLE_QUIZ=true
ENABLE_HOMEWORK_CHECK=true

# Audio
MAX_AUDIO_SIZE_MB=10
TTS_PROVIDER=openai

# Avatar
AVATAR_PROVIDER=local
DEFAULT_AVATAR_TEMPLATE=teacher_1
```

### Agent Configuration

Each agent can be configured independently:

- **Session Manager**: Session timeout, context window size
- **STT Agent**: Language models, confidence thresholds
- **Teaching Agent**: Response styles, persona settings
- **TTS Agent**: Voice styles, emotion modifications
- **Avatar Coordinator**: Animation quality, gesture mapping

## 📚 Usage

### Basic Chat Interface

1. **Start a session**: The app automatically creates a new session
2. **Type or speak**: Use text input or voice recording
3. **Get responses**: AI provides contextual, educational responses
4. **View avatar**: Toggle avatar display for visual interaction

### Quiz Generation

1. **Select subject**: Choose from Math, Science, Programming, etc.
2. **Set difficulty**: Easy, Medium, or Hard
3. **Take quiz**: Answer questions with immediate feedback
4. **Review results**: See detailed explanations and scores

### Homework Review

1. **Upload files**: Images, PDFs, or text files
2. **Select subject**: Specify the subject area
3. **Get feedback**: Receive detailed review and suggestions
4. **Improve work**: Use feedback to enhance your homework

### Settings Management

1. **Personal preferences**: Name, language, persona
2. **Audio settings**: Voice style, volume, speed
3. **Visual settings**: Theme, avatar, animations
4. **Privacy settings**: Data collection, analytics

## 🔄 API Endpoints

### Session Management
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{session_id}` - Get session details
- `PATCH /api/sessions/{session_id}` - Update session

### Audio Processing
- `POST /api/audio/transcribe` - Convert speech to text
- `POST /api/audio/stream` - Stream audio processing

### Text Processing
- `POST /api/text/process` - Process text input

### Quiz System
- `POST /api/quiz/generate` - Generate quiz
- `POST /api/quiz/submit` - Submit quiz answers

### Homework Checking
- `POST /api/homework/check` - Check uploaded homework

### WebSocket
- `WS /ws/{session_id}` - Real-time communication

## 🧠 Agent Workflows

### Flow A: Live Question (Synchronous)
1. User speaks → STT Agent
2. Language Detection → Intent Router
3. Teaching Agent → Response Synthesizer
4. TTS Agent → Avatar Coordinator
5. Response delivered to user

### Flow B: Homework Upload (Asynchronous)
1. File upload → OCR processing
2. Content analysis → RAG retrieval
3. Homework Checker → Background processing
4. Results notification → User feedback

### Flow C: Quiz Generation
1. Quiz request → Intent Router
2. Quiz Agent → Question generation
3. User answers → Evaluation Agent
4. Results → Feedback and remediation

## 🔒 Security & Privacy

- **Data Encryption**: All sensitive data encrypted at rest
- **Rate Limiting**: Protection against abuse and spam
- **Input Validation**: Comprehensive input sanitization
- **Session Management**: Secure session handling
- **Privacy Controls**: User-configurable data collection

## 📊 Monitoring & Analytics

- **Performance Metrics**: Response times, success rates
- **Usage Analytics**: Feature usage, user engagement
- **Error Tracking**: Comprehensive error logging
- **Health Checks**: System status monitoring

## 🚀 Deployment

### Docker Deployment

1. **Build images**
   ```bash
   docker-compose build
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

### Production Considerations

- Use PostgreSQL for production database
- Set up Redis cluster for caching
- Configure load balancer for scaling
- Set up monitoring and logging
- Use CDN for static assets
- Configure SSL/TLS certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation

## 🔮 Roadmap

### Upcoming Features
- [ ] Advanced avatar customization
- [ ] Multi-user collaboration
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Integration with learning management systems
- [ ] Advanced homework checking with AI vision
- [ ] Real-time collaboration features
- [ ] Advanced personalization algorithms

### Performance Improvements
- [ ] Caching optimization
- [ ] Database query optimization
- [ ] Audio processing improvements
- [ ] Avatar rendering optimization
- [ ] Real-time streaming enhancements

---

Built with ❤️ using FastAPI, React, LangChain, and LangGraph.

