import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import logging
from models.schemas import SessionCreate, SessionResponse, Language, Persona, MemoryEntry, ContextWindow

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions, context, and short-term memory"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.context_windows: Dict[str, ContextWindow] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
    async def create_session(
        self, 
        user_id: str, 
        language: Language = Language.ENGLISH,
        persona: Persona = Persona.FRIENDLY
    ) -> SessionResponse:
        """Create a new tutoring session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "language": language,
                "persona": persona,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "context_window": [],
                "rate_limit_count": 0,
                "rate_limit_reset": datetime.now() + timedelta(minutes=1)
            }
            
            # Store session
            self.sessions[session_id] = session_data
            
            # Initialize context window
            self.context_windows[session_id] = ContextWindow(
                session_id=session_id,
                entries=[],
                max_size=10
            )
            
            # Initialize rate limiting
            self.rate_limits[session_id] = {
                "requests": 0,
                "reset_time": datetime.now() + timedelta(minutes=1),
                "max_requests": 60  # 60 requests per minute
            }
            
            logger.info(f"Created session {session_id} for user {user_id}")
            
            return SessionResponse(
                session_id=session_id,
                user_id=user_id,
                language=language,
                persona=persona,
                created_at=session_data["created_at"],
                context_window=session_data["context_window"]
            )
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get session details"""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                return None
                
            return SessionResponse(
                session_id=session_data["session_id"],
                user_id=session_data["user_id"],
                language=session_data["language"],
                persona=session_data["persona"],
                created_at=session_data["created_at"],
                context_window=session_data["context_window"]
            )
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update last activity timestamp"""
        try:
            if session_id in self.sessions:
                self.sessions[session_id]["last_activity"] = datetime.now()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            return False
    
    async def add_to_context(
        self, 
        session_id: str, 
        entry_type: str, 
        content: str, 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add entry to session context window"""
        try:
            if session_id not in self.context_windows:
                return False
                
            context_window = self.context_windows[session_id]
            
            # Create new memory entry
            entry = MemoryEntry(
                timestamp=datetime.now(),
                type=entry_type,
                content=content,
                metadata=metadata or {}
            )
            
            # Add to context window
            context_window.entries.append(entry)
            
            # Maintain sliding window size
            if len(context_window.entries) > context_window.max_size:
                context_window.entries = context_window.entries[-context_window.max_size:]
            
            # Update session context
            if session_id in self.sessions:
                self.sessions[session_id]["context_window"] = [
                    {
                        "timestamp": entry.timestamp.isoformat(),
                        "type": entry.type,
                        "content": entry.content,
                        "metadata": entry.metadata
                    }
                    for entry in context_window.entries
                ]
            
            logger.debug(f"Added {entry_type} entry to context for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to context: {e}")
            return False
    
    async def get_context(self, session_id: str) -> List[Dict[str, Any]]:
        """Get current context window"""
        try:
            if session_id not in self.context_windows:
                return []
                
            context_window = self.context_windows[session_id]
            return [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "type": entry.type,
                    "content": entry.content,
                    "metadata": entry.metadata
                }
                for entry in context_window.entries
            ]
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return []
    
    async def check_rate_limit(self, session_id: str) -> bool:
        """Check if session is within rate limits"""
        try:
            if session_id not in self.rate_limits:
                return True
                
            rate_limit = self.rate_limits[session_id]
            now = datetime.now()
            
            # Reset counter if time window has passed
            if now >= rate_limit["reset_time"]:
                rate_limit["requests"] = 0
                rate_limit["reset_time"] = now + timedelta(minutes=1)
            
            # Check if within limits
            if rate_limit["requests"] >= rate_limit["max_requests"]:
                return False
                
            # Increment counter
            rate_limit["requests"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow on error
    
    async def get_session_config(self, session_id: str) -> Dict[str, Any]:
        """Get session configuration for agents"""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                return {}
                
            return {
                "session_id": session_data["session_id"],
                "user_id": session_data["user_id"],
                "language": session_data["language"],
                "persona": session_data["persona"],
                "context": await self.get_context(session_id),
                "rate_limit_ok": await self.check_rate_limit(session_id)
            }
        except Exception as e:
            logger.error(f"Error getting session config: {e}")
            return {}
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old sessions"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            sessions_to_remove = []
            
            for session_id, session_data in self.sessions.items():
                if session_data["last_activity"] < cutoff_time:
                    sessions_to_remove.append(session_id)
            
            # Remove old sessions
            for session_id in sessions_to_remove:
                self.sessions.pop(session_id, None)
                self.context_windows.pop(session_id, None)
                self.rate_limits.pop(session_id, None)
            
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
            return len(sessions_to_remove)
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            return 0
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            active_sessions = len(self.sessions)
            total_context_entries = sum(
                len(cw.entries) for cw in self.context_windows.values()
            )
            
            return {
                "active_sessions": active_sessions,
                "total_context_entries": total_context_entries,
                "memory_usage_mb": len(str(self.sessions)) / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {}