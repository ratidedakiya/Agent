import logging
from typing import Dict, List, Optional, Any
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from models.schemas import (
    Subject, Persona, Language, TeachingAgentResponse, 
    AgentRequest, Emotion, GestureTag
)

logger = logging.getLogger(__name__)

class TeachingAgent:
    """Teaching agent with subject-specific expertise and persona-based responses"""
    
    def __init__(self, openai_api_key: str):
        self.llm = OpenAI(
            openai_api_key=openai_api_key,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Subject-specific prompt templates
        self.subject_templates = {
            Subject.MATH: {
                'system_prompt': """You are an expert mathematics tutor. Your role is to:
1. Explain mathematical concepts clearly and step-by-step
2. Break down complex problems into manageable steps
3. Use visual descriptions and analogies when helpful
4. Encourage students and build their confidence
5. Ask guiding questions to help students think through problems
6. Provide practice problems when appropriate

Always show your work and explain each step clearly.""",
                'response_style': 'step_by_step',
                'examples': [
                    "Let's solve this step by step...",
                    "First, let's identify what we're looking for...",
                    "Remember the formula: ...",
                    "Let's check our answer by substituting back..."
                ]
            },
            Subject.SCIENCE: {
                'system_prompt': """You are an expert science tutor covering physics, chemistry, and biology. Your role is to:
1. Explain scientific concepts with real-world examples
2. Connect theory to practical applications
3. Use analogies and visual descriptions
4. Encourage scientific thinking and questioning
5. Explain the 'why' behind scientific phenomena
6. Use appropriate scientific terminology

Make science accessible and engaging.""",
                'response_style': 'explanatory',
                'examples': [
                    "Let's think about this scientifically...",
                    "Here's a real-world example...",
                    "The key principle here is...",
                    "Let's break this down into its components..."
                ]
            },
            Subject.PROGRAMMING: {
                'system_prompt': """You are an expert programming tutor. Your role is to:
1. Explain programming concepts with clear examples
2. Show code with proper syntax and best practices
3. Explain the logic and reasoning behind code
4. Help debug and troubleshoot issues
5. Encourage good coding practices
6. Provide hands-on exercises

Always include working code examples and explain the logic.""",
                'response_style': 'code_focused',
                'examples': [
                    "Let's look at the code...",
                    "Here's how we can implement this...",
                    "The key concept here is...",
                    "Let's debug this step by step..."
                ]
            },
            Subject.HISTORY: {
                'system_prompt': """You are an expert history tutor. Your role is to:
1. Present historical events in context
2. Explain cause and effect relationships
3. Connect past events to present situations
4. Use primary sources and evidence
5. Encourage critical thinking about historical narratives
6. Make history engaging and relevant

Present multiple perspectives when appropriate.""",
                'response_style': 'narrative',
                'examples': [
                    "Let's put this in historical context...",
                    "The key factors that led to this were...",
                    "This connects to what we learned about...",
                    "Let's examine the evidence..."
                ]
            },
            Subject.LITERATURE: {
                'system_prompt': """You are an expert literature tutor. Your role is to:
1. Analyze literary works and themes
2. Explain literary devices and techniques
3. Connect literature to broader themes and contexts
4. Encourage personal interpretation and critical thinking
5. Discuss character development and plot structure
6. Explore the author's purpose and message

Encourage students to form their own interpretations.""",
                'response_style': 'analytical',
                'examples': [
                    "Let's analyze this passage...",
                    "The author uses this technique to...",
                    "What themes do you notice here?",
                    "Let's consider the character's motivation..."
                ]
            },
            Subject.GENERAL: {
                'system_prompt': """You are a knowledgeable and helpful tutor. Your role is to:
1. Provide clear, accurate explanations
2. Adapt your teaching style to the student's needs
3. Encourage questions and critical thinking
4. Use examples and analogies to clarify concepts
5. Build confidence and motivation
6. Provide additional resources when helpful

Be encouraging and supportive while maintaining academic rigor.""",
                'response_style': 'adaptive',
                'examples': [
                    "Let me help you understand this...",
                    "That's a great question!",
                    "Here's another way to think about it...",
                    "Let's work through this together..."
                ]
            }
        }
        
        # Persona-based response styles
        self.persona_styles = {
            Persona.FRIENDLY: {
                'tone': 'warm and encouraging',
                'greetings': ['Hi there!', 'Hello!', 'Great to see you!'],
                'encouragement': ['You\'re doing great!', 'Keep it up!', 'That\'s exactly right!'],
                'corrections': ['Let\'s try a different approach...', 'No worries, let\'s work through this...']
            },
            Persona.PROFESSIONAL: {
                'tone': 'clear and structured',
                'greetings': ['Good day.', 'Hello.', 'How can I assist you?'],
                'encouragement': ['Well done.', 'Correct.', 'Good work.'],
                'corrections': ['Let me clarify...', 'The correct approach is...']
            },
            Persona.ENCOURAGING: {
                'tone': 'motivational and supportive',
                'greetings': ['Welcome!', 'Ready to learn?', 'Let\'s do this!'],
                'encouragement': ['Fantastic!', 'You\'ve got this!', 'Amazing work!'],
                'corrections': ['Don\'t worry, everyone learns at their own pace...', 'Let\'s try again together...']
            },
            Persona.STRICT: {
                'tone': 'direct and focused',
                'greetings': ['Let\'s begin.', 'Focus now.', 'Time to work.'],
                'encouragement': ['Acceptable.', 'Correct.', 'Good.'],
                'corrections': ['That\'s incorrect. The proper method is...', 'You need to...']
            }
        }
        
        # Memory for conversation context
        self.memories: Dict[str, ConversationBufferWindowMemory] = {}
    
    async def generate_response(
        self, 
        request: AgentRequest,
        context: List[Dict[str, Any]] = None
    ) -> TeachingAgentResponse:
        """Generate teaching response based on request and context"""
        try:
            # Get subject configuration
            subject_config = self.subject_templates.get(request.subject, self.subject_templates[Subject.GENERAL])
            persona_config = self.persona_styles.get(Persona.FRIENDLY)  # Default persona
            
            # Build context string
            context_str = self._build_context_string(context or [])
            
            # Create prompt template
            prompt_template = self._create_prompt_template(subject_config, persona_config)
            
            # Get or create memory for session
            memory = self._get_memory(request.session_id)
            
            # Create prompt
            prompt = prompt_template.format(
                subject=request.subject.value,
                question=request.text,
                context=context_str,
                persona_tone=persona_config['tone']
            )
            
            # Generate response using LangChain
            response = await self._generate_with_langchain(prompt, memory)
            
            # Parse response
            parsed_response = self._parse_response(response, request.subject)
            
            # Add to memory
            memory.save_context(
                {"input": request.text},
                {"output": parsed_response['text']}
            )
            
            logger.info(f"Generated teaching response for {request.subject} subject")
            return TeachingAgentResponse(**parsed_response)
            
        except Exception as e:
            logger.error(f"Error generating teaching response: {e}")
            return TeachingAgentResponse(
                text="I apologize, but I'm having trouble processing your request. Could you please try again?",
                summary="Error in processing",
                confidence=0.0,
                need_steps=False,
                citations=[]
            )
    
    def _create_prompt_template(self, subject_config: Dict, persona_config: Dict) -> str:
        """Create prompt template based on subject and persona"""
        template = f"""
{subject_config['system_prompt']}

Persona: Be {persona_config['tone']} in your responses.

Context from previous conversation:
{{context}}

Current question: {{question}}

Please provide a helpful, educational response. If the question requires step-by-step explanation, break it down clearly. If it's a simple question, provide a concise answer. Always be encouraging and supportive.

Response format:
- Start with a brief acknowledgment
- Provide the main explanation
- Include examples if helpful
- End with encouragement or next steps
"""
        return template
    
    def _build_context_string(self, context: List[Dict[str, Any]]) -> str:
        """Build context string from conversation history"""
        if not context:
            return "No previous context available."
        
        context_parts = []
        for entry in context[-5:]:  # Last 5 entries
            if entry.get('type') in ['question', 'answer']:
                context_parts.append(f"{entry['type']}: {entry['content']}")
        
        return "\n".join(context_parts) if context_parts else "No relevant context available."
    
    async def _generate_with_langchain(self, prompt: str, memory: ConversationBufferWindowMemory) -> str:
        """Generate response using LangChain"""
        try:
            # Create chain
            chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate.from_template(prompt),
                memory=memory
            )
            
            # Generate response
            response = await chain.arun(input="")
            return response
            
        except Exception as e:
            logger.error(f"Error in LangChain generation: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def _parse_response(self, response: str, subject: Subject) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Determine if steps are needed based on subject and content
            step_indicators = ['step', 'first', 'next', 'then', 'finally', 'solve', 'calculate']
            need_steps = any(indicator in response.lower() for indicator in step_indicators)
            
            # Extract summary (first sentence or first 100 characters)
            sentences = response.split('.')
            summary = sentences[0].strip() if sentences else response[:100]
            
            # Determine confidence based on response length and clarity
            confidence = min(len(response) / 200, 1.0)  # Longer responses are more confident
            
            # Extract citations (look for patterns like [1], (source), etc.)
            citations = []
            import re
            citation_patterns = [
                r'\[(\d+)\]',
                r'\(([^)]+)\)',
                r'according to ([^,]+)',
                r'as stated in ([^,]+)'
            ]
            
            for pattern in citation_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                citations.extend(matches)
            
            return {
                'text': response,
                'summary': summary,
                'confidence': confidence,
                'need_steps': need_steps,
                'citations': citations
            }
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {
                'text': response,
                'summary': response[:100],
                'confidence': 0.5,
                'need_steps': False,
                'citations': []
            }
    
    def _get_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        """Get or create memory for session"""
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferWindowMemory(
                k=10,  # Keep last 10 exchanges
                return_messages=True
            )
        return self.memories[session_id]
    
    async def get_subject_expertise(self, subject: Subject) -> Dict[str, Any]:
        """Get information about subject expertise"""
        return self.subject_templates.get(subject, self.subject_templates[Subject.GENERAL])
    
    async def update_persona(self, session_id: str, persona: Persona) -> bool:
        """Update persona for a specific session"""
        try:
            # This would typically update the prompt template for the session
            # For now, we'll just log the change
            logger.info(f"Updated persona for session {session_id} to {persona}")
            return True
        except Exception as e:
            logger.error(f"Error updating persona: {e}")
            return False
    
    async def clear_memory(self, session_id: str) -> bool:
        """Clear conversation memory for session"""
        try:
            if session_id in self.memories:
                self.memories[session_id].clear()
                logger.info(f"Cleared memory for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False
    
    async def get_memory_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation memory"""
        try:
            if session_id not in self.memories:
                return {'message_count': 0, 'topics': []}
            
            memory = self.memories[session_id]
            messages = memory.chat_memory.messages
            
            # Extract topics from messages
            topics = []
            for message in messages[-10:]:  # Last 10 messages
                if isinstance(message, HumanMessage):
                    # Simple topic extraction (first few words)
                    words = message.content.split()[:5]
                    topics.append(' '.join(words))
            
            return {
                'message_count': len(messages),
                'topics': topics,
                'last_activity': messages[-1].additional_kwargs.get('timestamp') if messages else None
            }
            
        except Exception as e:
            logger.error(f"Error getting memory summary: {e}")
            return {'message_count': 0, 'topics': []}