import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from models.schemas import (
    AudioResponse, TextResponse, QuizResponse, HomeworkResponse,
    Language, Subject, Intent, Emotion, GestureTag
)
from agents.session_manager import SessionManager
from agents.stt_agent import STTAgent
from agents.language_detector import LanguageDetector
from agents.intent_router import IntentRouter
from agents.teaching_agent import TeachingAgent
from agents.response_synthesizer import ResponseSynthesizer
from agents.tts_agent import TTSAgent
from agents.avatar_coordinator import AvatarCoordinator

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Main orchestrator that coordinates all agents using LangGraph"""
    
    def __init__(self, openai_api_key: str = None):
        # Initialize all agents
        self.session_manager = SessionManager()
        self.stt_agent = STTAgent()
        self.language_detector = LanguageDetector()
        self.intent_router = IntentRouter()
        self.teaching_agent = TeachingAgent(openai_api_key)
        self.response_synthesizer = ResponseSynthesizer()
        self.tts_agent = TTSAgent(openai_api_key)
        self.avatar_coordinator = AvatarCoordinator()
        
        # Build the agent graph
        self.graph = self._build_agent_graph()
    
    def _build_agent_graph(self) -> StateGraph:
        """Build the LangGraph workflow for agent coordination"""
        
        # Define the state structure
        class AgentState:
            def __init__(self):
                self.messages: List[BaseMessage] = []
                self.session_id: Optional[str] = None
                self.user_id: Optional[str] = None
                self.audio_data: Optional[bytes] = None
                self.transcript: Optional[str] = None
                self.language: Optional[Language] = None
                self.normalized_text: Optional[str] = None
                self.intent: Optional[Intent] = None
                self.subject: Optional[Subject] = None
                self.priority: Optional[str] = None
                self.context: List[Dict[str, Any]] = []
                self.teaching_response: Optional[Dict[str, Any]] = None
                self.synthesized_response: Optional[Dict[str, Any]] = None
                self.tts_output: Optional[Dict[str, Any]] = None
                self.avatar_output: Optional[Dict[str, Any]] = None
                self.final_response: Optional[Dict[str, Any]] = None
                self.error: Optional[str] = None
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("session_manager", self._session_manager_node)
        workflow.add_node("stt_agent", self._stt_agent_node)
        workflow.add_node("language_detector", self._language_detector_node)
        workflow.add_node("intent_router", self._intent_router_node)
        workflow.add_node("teaching_agent", self._teaching_agent_node)
        workflow.add_node("response_synthesizer", self._response_synthesizer_node)
        workflow.add_node("tts_agent", self._tts_agent_node)
        workflow.add_node("avatar_coordinator", self._avatar_coordinator_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Define the workflow edges
        workflow.set_entry_point("session_manager")
        
        # Audio processing flow
        workflow.add_edge("session_manager", "stt_agent")
        workflow.add_edge("stt_agent", "language_detector")
        workflow.add_edge("language_detector", "intent_router")
        workflow.add_edge("intent_router", "teaching_agent")
        workflow.add_edge("teaching_agent", "response_synthesizer")
        workflow.add_edge("response_synthesizer", "tts_agent")
        workflow.add_edge("tts_agent", "avatar_coordinator")
        workflow.add_edge("avatar_coordinator", END)
        
        # Error handling
        workflow.add_edge("error_handler", END)
        
        return workflow.compile()
    
    async def process_audio(
        self,
        audio_data: bytes,
        session_id: Optional[str] = None,
        language_hint: Optional[Language] = None
    ) -> AudioResponse:
        """Process audio input through the full pipeline"""
        try:
            # Create initial state
            initial_state = {
                "audio_data": audio_data,
                "session_id": session_id,
                "language": language_hint
            }
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Extract and return the final response
            if result.get("error"):
                raise Exception(result["error"])
            
            return AudioResponse(
                transcript=result.get("transcript", ""),
                language=result.get("language", Language.ENGLISH),
                confidence=result.get("confidence", 0.0),
                timings=result.get("timings", [])
            )
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise
    
    async def process_text(
        self,
        text: str,
        session_id: str,
        language: Optional[Language] = None
    ) -> TextResponse:
        """Process text input through the pipeline"""
        try:
            # Create initial state
            initial_state = {
                "transcript": text,
                "session_id": session_id,
                "language": language or Language.ENGLISH
            }
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Extract and return the final response
            if result.get("error"):
                raise Exception(result["error"])
            
            return TextResponse(
                text=result.get("final_response", {}).get("text", ""),
                summary=result.get("final_response", {}).get("summary"),
                confidence=result.get("final_response", {}).get("confidence", 0.0),
                need_steps=result.get("final_response", {}).get("need_steps", False),
                citations=result.get("final_response", {}).get("citations", []),
                voice_style=result.get("final_response", {}).get("voice_style", "friendly_male"),
                emotion=result.get("final_response", {}).get("emotion", Emotion.NEUTRAL),
                gesture_tag=result.get("final_response", {}).get("gesture_tag", GestureTag.AFFIRMATIVE),
                emphasis_spans=result.get("final_response", {}).get("emphasis_spans", [])
            )
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise
    
    async def generate_quiz(
        self,
        topic: str,
        difficulty: str,
        subject: Subject,
        session_id: str
    ) -> QuizResponse:
        """Generate a quiz using the teaching agent"""
        try:
            # This would be a specialized flow for quiz generation
            # For now, we'll use the teaching agent
            from models.schemas import AgentRequest
            
            request = AgentRequest(
                session_id=session_id,
                user_id="quiz_user",
                text=f"Generate a quiz about {topic} at {difficulty} level",
                language="en",
                subject=subject
            )
            
            response = await self.teaching_agent.generate_response(request)
            
            # Convert teaching response to quiz format
            # This is a simplified conversion
            return QuizResponse(
                quiz_id=f"quiz_{session_id}",
                questions=[],  # Would be parsed from teaching response
                time_limit=300,
                instructions="Answer the following questions based on the topic."
            )
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            raise
    
    async def check_homework(
        self,
        file_data: bytes,
        file_type: str,
        subject: Subject,
        session_id: str
    ) -> HomeworkResponse:
        """Check uploaded homework"""
        try:
            # This would be a specialized flow for homework checking
            # For now, return a mock response
            return HomeworkResponse(
                verdict="correct",
                score=85.0,
                short_reason="Good work overall with minor errors",
                detailed_explanation="Your solution shows good understanding of the concepts...",
                suggestions=["Check your calculations in step 3", "Review the formula for area"],
                confidence=0.8
            )
            
        except Exception as e:
            logger.error(f"Error checking homework: {e}")
            raise
    
    # Node implementations for the graph
    async def _session_manager_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Session manager node"""
        try:
            session_id = state.get("session_id")
            if not session_id:
                # Create new session
                session = await self.session_manager.create_session(
                    user_id="anonymous",
                    language=state.get("language", Language.ENGLISH)
                )
                session_id = session.session_id
            
            # Get session context
            context = await self.session_manager.get_context(session_id)
            
            return {
                "session_id": session_id,
                "context": context
            }
        except Exception as e:
            logger.error(f"Error in session manager node: {e}")
            return {"error": str(e)}
    
    async def _stt_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """STT agent node"""
        try:
            audio_data = state.get("audio_data")
            if not audio_data:
                return {"error": "No audio data provided"}
            
            language_hint = state.get("language")
            result = await self.stt_agent.transcribe_audio(
                audio_data=audio_data,
                language_hint=language_hint
            )
            
            return {
                "transcript": result.transcript,
                "language": result.language,
                "confidence": result.confidence,
                "timings": result.timings
            }
        except Exception as e:
            logger.error(f"Error in STT agent node: {e}")
            return {"error": str(e)}
    
    async def _language_detector_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Language detector node"""
        try:
            transcript = state.get("transcript")
            if not transcript:
                return {"error": "No transcript provided"}
            
            language_hint = state.get("language")
            detected_language, confidence = await self.language_detector.detect_language(
                transcript, language_hint
            )
            
            normalized_text = await self.language_detector.normalize_text(
                transcript, detected_language
            )
            
            return {
                "language": detected_language,
                "normalized_text": normalized_text
            }
        except Exception as e:
            logger.error(f"Error in language detector node: {e}")
            return {"error": str(e)}
    
    async def _intent_router_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Intent router node"""
        try:
            text = state.get("normalized_text") or state.get("transcript")
            if not text:
                return {"error": "No text provided"}
            
            context = state.get("context", [])
            routing = await self.intent_router.route_request(text, context)
            
            return {
                "intent": routing["intent"],
                "subject": routing["subject"],
                "priority": routing["priority"]
            }
        except Exception as e:
            logger.error(f"Error in intent router node: {e}")
            return {"error": str(e)}
    
    async def _teaching_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Teaching agent node"""
        try:
            text = state.get("normalized_text") or state.get("transcript")
            if not text:
                return {"error": "No text provided"}
            
            from models.schemas import AgentRequest
            
            request = AgentRequest(
                session_id=state["session_id"],
                user_id="user",
                text=text,
                language=state.get("language", Language.ENGLISH).value,
                subject=state.get("subject", Subject.GENERAL),
                context=state.get("context", [])
            )
            
            response = await self.teaching_agent.generate_response(request)
            
            return {
                "teaching_response": {
                    "text": response.text,
                    "summary": response.summary,
                    "confidence": response.confidence,
                    "need_steps": response.need_steps,
                    "citations": response.citations
                }
            }
        except Exception as e:
            logger.error(f"Error in teaching agent node: {e}")
            return {"error": str(e)}
    
    async def _response_synthesizer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Response synthesizer node"""
        try:
            teaching_response = state.get("teaching_response")
            if not teaching_response:
                return {"error": "No teaching response provided"}
            
            from models.schemas import ResponseSynthesizerInput
            
            input_data = ResponseSynthesizerInput(
                text=teaching_response["text"],
                voice_style="friendly_male",
                language=state.get("language", Language.ENGLISH).value,
                emotion=Emotion.ENCOURAGING,
                gesture_tag=GestureTag.AFFIRMATIVE
            )
            
            response = await self.response_synthesizer.synthesize_response(input_data)
            
            return {
                "synthesized_response": {
                    "text": response.text,
                    "voice_style": response.voice_style,
                    "language": response.language,
                    "emotion": response.emotion,
                    "gesture_tag": response.gesture_tag,
                    "emphasis_spans": response.emphasis_spans
                }
            }
        except Exception as e:
            logger.error(f"Error in response synthesizer node: {e}")
            return {"error": str(e)}
    
    async def _tts_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """TTS agent node"""
        try:
            synthesized_response = state.get("synthesized_response")
            if not synthesized_response:
                return {"error": "No synthesized response provided"}
            
            tts_output = await self.tts_agent.synthesize_speech(
                text=synthesized_response["text"],
                voice_style=synthesized_response["voice_style"],
                language=Language(synthesized_response["language"]),
                emotion=synthesized_response["emotion"]
            )
            
            return {
                "tts_output": {
                    "audio_data": tts_output.audio_data,
                    "phoneme_timestamps": tts_output.phoneme_timestamps
                }
            }
        except Exception as e:
            logger.error(f"Error in TTS agent node: {e}")
            return {"error": str(e)}
    
    async def _avatar_coordinator_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Avatar coordinator node"""
        try:
            tts_output = state.get("tts_output")
            synthesized_response = state.get("synthesized_response")
            
            if not tts_output or not synthesized_response:
                return {"error": "Missing TTS or synthesized response"}
            
            from models.schemas import TTSOutput, ResponseSynthesizerOutput
            
            tts_data = TTSOutput(
                audio_data=tts_output["audio_data"],
                phoneme_timestamps=tts_output["phoneme_timestamps"]
            )
            
            response_data = ResponseSynthesizerOutput(
                text=synthesized_response["text"],
                voice_style=synthesized_response["voice_style"],
                language=synthesized_response["language"],
                emotion=synthesized_response["emotion"],
                gesture_tag=synthesized_response["gesture_tag"],
                emphasis_spans=synthesized_response["emphasis_spans"]
            )
            
            avatar_output = await self.avatar_coordinator.generate_avatar(
                tts_output=tts_data,
                response_data=response_data
            )
            
            return {
                "avatar_output": {
                    "video_url": avatar_output.video_url,
                    "webrtc_token": avatar_output.webrtc_token,
                    "expected_delay_ms": avatar_output.expected_delay_ms,
                    "gesture_timeline": avatar_output.gesture_timeline
                },
                "final_response": {
                    "text": synthesized_response["text"],
                    "summary": state.get("teaching_response", {}).get("summary"),
                    "confidence": state.get("teaching_response", {}).get("confidence", 0.0),
                    "need_steps": state.get("teaching_response", {}).get("need_steps", False),
                    "citations": state.get("teaching_response", {}).get("citations", []),
                    "voice_style": synthesized_response["voice_style"],
                    "emotion": synthesized_response["emotion"],
                    "gesture_tag": synthesized_response["gesture_tag"],
                    "emphasis_spans": synthesized_response["emphasis_spans"],
                    "video_url": avatar_output.video_url,
                    "audio_data": tts_output["audio_data"]
                }
            }
        except Exception as e:
            logger.error(f"Error in avatar coordinator node: {e}")
            return {"error": str(e)}
    
    async def _error_handler_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Error handler node"""
        error = state.get("error", "Unknown error occurred")
        logger.error(f"Error in agent pipeline: {error}")
        
        return {
            "final_response": {
                "text": "I apologize, but I encountered an error processing your request. Please try again.",
                "summary": "Error occurred",
                "confidence": 0.0,
                "need_steps": False,
                "citations": [],
                "voice_style": "friendly_male",
                "emotion": Emotion.NEUTRAL,
                "gesture_tag": GestureTag.AFFIRMATIVE,
                "emphasis_spans": []
            },
            "error": error
        }