from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio
import json
from typing import Dict, List, Optional
import logging

from agents.session_manager import SessionManager
from agents.orchestrator import AgentOrchestrator
from models.schemas import (
    SessionCreate, SessionResponse, 
    AudioRequest, AudioResponse,
    TextRequest, TextResponse,
    QuizRequest, QuizResponse,
    HomeworkRequest, HomeworkResponse
)
from database.connection import get_db
from utils.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
session_manager = None
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global session_manager, orchestrator
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    logger.info("AI Tutor application started")
    yield
    
    # Cleanup on shutdown
    logger.info("AI Tutor application shutting down")

app = FastAPI(
    title="AI Tutor API",
    description="Multi-agent AI tutoring system with voice and avatar support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get session manager
def get_session_manager() -> SessionManager:
    if session_manager is None:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    return session_manager

# Dependency to get orchestrator
def get_orchestrator() -> AgentOrchestrator:
    if orchestrator is None:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    return orchestrator

@app.get("/")
async def root():
    return {"message": "AI Tutor API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": "active"}

# Session Management
@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    sm: SessionManager = Depends(get_session_manager)
):
    """Create a new tutoring session"""
    try:
        session = await sm.create_session(
            user_id=session_data.user_id,
            language=session_data.language,
            persona=session_data.persona
        )
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    sm: SessionManager = Depends(get_session_manager)
):
    """Get session details"""
    try:
        session = await sm.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Audio Processing
@app.post("/api/audio/transcribe", response_model=AudioResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    session_id: str = None,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Convert speech to text"""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process through orchestrator
        result = await orchestrator.process_audio(
            audio_data=audio_data,
            session_id=session_id,
            language_hint=None
        )
        
        return result
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Text Processing
@app.post("/api/text/process", response_model=TextResponse)
async def process_text(
    request: TextRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Process text input and generate response"""
    try:
        result = await orchestrator.process_text(
            text=request.text,
            session_id=request.session_id,
            language=request.language
        )
        return result
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Quiz Generation
@app.post("/api/quiz/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Generate a quiz based on topic and difficulty"""
    try:
        result = await orchestrator.generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty,
            subject=request.subject,
            session_id=request.session_id
        )
        return result
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Homework Checking
@app.post("/api/homework/check", response_model=HomeworkResponse)
async def check_homework(
    homework_file: UploadFile = File(...),
    session_id: str = None,
    subject: str = "general",
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Check uploaded homework"""
    try:
        file_data = await homework_file.read()
        
        result = await orchestrator.check_homework(
            file_data=file_data,
            file_type=homework_file.content_type,
            subject=subject,
            session_id=session_id
        )
        
        return result
    except Exception as e:
        logger.error(f"Error checking homework: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket for real-time communication
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process through orchestrator
            if message["type"] == "audio":
                # Handle audio streaming
                result = await orchestrator.process_audio_stream(
                    audio_chunk=message["data"],
                    session_id=session_id
                )
            elif message["type"] == "text":
                # Handle text input
                result = await orchestrator.process_text(
                    text=message["data"],
                    session_id=session_id
                )
            
            # Send response back to client
            await websocket.send_text(json.dumps(result))
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

# Audio streaming endpoint
@app.post("/api/audio/stream")
async def stream_audio(
    audio_file: UploadFile = File(...),
    session_id: str = None,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Stream audio processing for real-time response"""
    try:
        async def generate_audio_response():
            # Read audio in chunks
            chunk_size = 1024
            while True:
                chunk = await audio_file.read(chunk_size)
                if not chunk:
                    break
                
                # Process chunk
                result = await orchestrator.process_audio_chunk(
                    audio_chunk=chunk,
                    session_id=session_id
                )
                
                if result:
                    yield f"data: {json.dumps(result)}\n\n"
        
        return StreamingResponse(
            generate_audio_response(),
            media_type="text/plain"
        )
    except Exception as e:
        logger.error(f"Error streaming audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)