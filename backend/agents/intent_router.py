import re
import logging
from typing import Dict, List, Optional, Tuple
from models.schemas import Intent, Subject, Language

logger = logging.getLogger(__name__)

class IntentRouter:
    """Intent classification and routing agent"""
    
    def __init__(self):
        # Intent patterns and keywords
        self.intent_patterns = {
            Intent.ASK: {
                'keywords': ['what', 'how', 'why', 'when', 'where', 'explain', 'tell me', 'show me', 'help'],
                'patterns': [
                    r'what is',
                    r'how do',
                    r'why does',
                    r'explain',
                    r'tell me about',
                    r'show me how',
                    r'help me understand',
                    r'can you explain',
                    r'what does.*mean',
                    r'how does.*work'
                ],
                'priority': 'normal'
            },
            Intent.CHECK_HOMEWORK: {
                'keywords': ['check', 'grade', 'review', 'homework', 'assignment', 'solution', 'answer'],
                'patterns': [
                    r'check my',
                    r'grade my',
                    r'review my',
                    r'homework',
                    r'assignment',
                    r'is this correct',
                    r'did i get this right',
                    r'check my work',
                    r'verify my answer'
                ],
                'priority': 'normal'
            },
            Intent.START_QUIZ: {
                'keywords': ['quiz', 'test', 'practice', 'questions', 'exam', 'challenge'],
                'patterns': [
                    r'give me a quiz',
                    r'quiz me on',
                    r'test my knowledge',
                    r'practice questions',
                    r'challenge me',
                    r'create a quiz',
                    r'generate questions',
                    r'quiz time'
                ],
                'priority': 'normal'
            },
            Intent.SMALL_TALK: {
                'keywords': ['hello', 'hi', 'how are you', 'good morning', 'good afternoon', 'thanks', 'thank you'],
                'patterns': [
                    r'hello',
                    r'hi there',
                    r'how are you',
                    r'good morning',
                    r'good afternoon',
                    r'thanks',
                    r'thank you',
                    r'nice to meet you',
                    r'how\'s it going'
                ],
                'priority': 'background'
            },
            Intent.ESCALATE: {
                'keywords': ['help', 'stuck', 'confused', 'don\'t understand', 'too hard', 'difficult'],
                'patterns': [
                    r'i\'m stuck',
                    r'i don\'t understand',
                    r'this is too hard',
                    r'it\'s too difficult',
                    r'i need help',
                    r'can\'t figure out',
                    r'i\'m confused',
                    r'this doesn\'t make sense'
                ],
                'priority': 'urgent'
            }
        }
        
        # Subject patterns and keywords
        self.subject_patterns = {
            Subject.MATH: {
                'keywords': ['math', 'mathematics', 'algebra', 'geometry', 'calculus', 'equation', 'solve', 'calculate'],
                'patterns': [
                    r'\d+\s*[+\-*/]\s*\d+',  # Basic arithmetic
                    r'equation',
                    r'solve for',
                    r'calculate',
                    r'geometry',
                    r'algebra',
                    r'calculus',
                    r'derivative',
                    r'integral',
                    r'quadratic',
                    r'polynomial'
                ]
            },
            Subject.SCIENCE: {
                'keywords': ['science', 'physics', 'chemistry', 'biology', 'experiment', 'theory', 'hypothesis'],
                'patterns': [
                    r'physics',
                    r'chemistry',
                    r'biology',
                    r'experiment',
                    r'theory',
                    r'hypothesis',
                    r'molecule',
                    r'atom',
                    r'force',
                    r'energy',
                    r'evolution',
                    r'photosynthesis'
                ]
            },
            Subject.PROGRAMMING: {
                'keywords': ['programming', 'code', 'python', 'javascript', 'java', 'function', 'variable', 'algorithm'],
                'patterns': [
                    r'programming',
                    r'coding',
                    r'python',
                    r'javascript',
                    r'java',
                    r'function',
                    r'variable',
                    r'algorithm',
                    r'data structure',
                    r'loop',
                    r'if statement',
                    r'class',
                    r'object'
                ]
            },
            Subject.HISTORY: {
                'keywords': ['history', 'historical', 'war', 'revolution', 'ancient', 'medieval', 'timeline'],
                'patterns': [
                    r'history',
                    r'historical',
                    r'war',
                    r'revolution',
                    r'ancient',
                    r'medieval',
                    r'timeline',
                    r'century',
                    r'empire',
                    r'civilization'
                ]
            },
            Subject.LITERATURE: {
                'keywords': ['literature', 'book', 'novel', 'poetry', 'author', 'character', 'theme', 'plot'],
                'patterns': [
                    r'literature',
                    r'book',
                    r'novel',
                    r'poetry',
                    r'author',
                    r'character',
                    r'theme',
                    r'plot',
                    r'story',
                    r'poem',
                    r'writing'
                ]
            }
        }
        
        # Priority weights
        self.priority_weights = {
            'urgent': 3,
            'normal': 2,
            'background': 1
        }
    
    async def classify_intent(self, text: str, context: List[Dict[str, Any]] = None) -> Tuple[Intent, float, str]:
        """Classify user intent with confidence score and priority"""
        try:
            if not text.strip():
                return Intent.ASK, 0.0, 'normal'
            
            text_lower = text.lower()
            intent_scores = {}
            
            # Calculate scores for each intent
            for intent, config in self.intent_patterns.items():
                score = 0.0
                
                # Check keyword matches
                keyword_matches = sum(1 for keyword in config['keywords'] if keyword in text_lower)
                if keyword_matches > 0:
                    score += keyword_matches * 0.3
                
                # Check pattern matches
                pattern_matches = 0
                for pattern in config['patterns']:
                    if re.search(pattern, text_lower):
                        pattern_matches += 1
                
                if pattern_matches > 0:
                    score += pattern_matches * 0.5
                
                # Apply priority weight
                priority_weight = self.priority_weights.get(config['priority'], 1)
                score *= priority_weight
                
                intent_scores[intent] = score
            
            # Find best intent
            if not intent_scores or max(intent_scores.values()) == 0:
                # Default to ASK if no clear intent
                best_intent = Intent.ASK
                confidence = 0.1
                priority = 'normal'
            else:
                best_intent = max(intent_scores, key=intent_scores.get)
                confidence = min(intent_scores[best_intent] / 2.0, 1.0)  # Normalize to 0-1
                priority = self.intent_patterns[best_intent]['priority']
            
            # Check context for intent hints
            if context:
                context_hint = await self._analyze_context_for_intent(context)
                if context_hint and context_hint != best_intent:
                    # Adjust confidence based on context
                    confidence = max(confidence - 0.2, 0.1)
            
            logger.info(f"Classified intent: {best_intent} (confidence: {confidence:.2f}, priority: {priority})")
            return best_intent, confidence, priority
            
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return Intent.ASK, 0.0, 'normal'
    
    async def classify_subject(self, text: str, context: List[Dict[str, Any]] = None) -> Tuple[Subject, float]:
        """Classify subject area with confidence score"""
        try:
            if not text.strip():
                return Subject.GENERAL, 0.0
            
            text_lower = text.lower()
            subject_scores = {}
            
            # Calculate scores for each subject
            for subject, config in self.subject_patterns.items():
                score = 0.0
                
                # Check keyword matches
                keyword_matches = sum(1 for keyword in config['keywords'] if keyword in text_lower)
                if keyword_matches > 0:
                    score += keyword_matches * 0.4
                
                # Check pattern matches
                pattern_matches = 0
                for pattern in config['patterns']:
                    if re.search(pattern, text_lower):
                        pattern_matches += 1
                
                if pattern_matches > 0:
                    score += pattern_matches * 0.6
                
                subject_scores[subject] = score
            
            # Find best subject
            if not subject_scores or max(subject_scores.values()) == 0:
                best_subject = Subject.GENERAL
                confidence = 0.1
            else:
                best_subject = max(subject_scores, key=subject_scores.get)
                confidence = min(subject_scores[best_subject] / 2.0, 1.0)  # Normalize to 0-1
            
            # Check context for subject hints
            if context:
                context_hint = await self._analyze_context_for_subject(context)
                if context_hint and context_hint != best_subject:
                    # Adjust confidence based on context
                    confidence = max(confidence - 0.2, 0.1)
            
            logger.info(f"Classified subject: {best_subject} (confidence: {confidence:.2f})")
            return best_subject, confidence
            
        except Exception as e:
            logger.error(f"Error classifying subject: {e}")
            return Subject.GENERAL, 0.0
    
    async def route_request(
        self, 
        text: str, 
        context: List[Dict[str, Any]] = None
    ) -> Dict[str, any]:
        """Route request to appropriate agent based on intent and subject"""
        try:
            # Classify intent and subject
            intent, intent_confidence, priority = await self.classify_intent(text, context)
            subject, subject_confidence = await self.classify_subject(text, context)
            
            # Determine routing
            routing = {
                'intent': intent,
                'subject': subject,
                'priority': priority,
                'confidence': {
                    'intent': intent_confidence,
                    'subject': subject_confidence,
                    'overall': (intent_confidence + subject_confidence) / 2
                },
                'agent': self._get_target_agent(intent, subject),
                'requires_context': self._requires_context(intent, subject),
                'is_urgent': priority == 'urgent',
                'estimated_processing_time': self._estimate_processing_time(intent, subject)
            }
            
            logger.info(f"Routed request: {routing}")
            return routing
            
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return {
                'intent': Intent.ASK,
                'subject': Subject.GENERAL,
                'priority': 'normal',
                'confidence': {'intent': 0.0, 'subject': 0.0, 'overall': 0.0},
                'agent': 'teaching_agent',
                'requires_context': True,
                'is_urgent': False,
                'estimated_processing_time': 2.0
            }
    
    def _get_target_agent(self, intent: Intent, subject: Subject) -> str:
        """Get target agent based on intent and subject"""
        if intent == Intent.CHECK_HOMEWORK:
            return 'homework_checker'
        elif intent == Intent.START_QUIZ:
            return 'quiz_agent'
        elif intent == Intent.ESCALATE:
            return 'teaching_agent'  # Special handling for escalated requests
        else:
            return 'teaching_agent'
    
    def _requires_context(self, intent: Intent, subject: Subject) -> bool:
        """Determine if request requires context"""
        context_required_intents = [Intent.ASK, Intent.ESCALATE]
        context_required_subjects = [Subject.MATH, Subject.SCIENCE, Subject.PROGRAMMING]
        
        return intent in context_required_intents or subject in context_required_subjects
    
    def _estimate_processing_time(self, intent: Intent, subject: Subject) -> float:
        """Estimate processing time in seconds"""
        base_times = {
            Intent.ASK: 2.0,
            Intent.CHECK_HOMEWORK: 5.0,
            Intent.START_QUIZ: 3.0,
            Intent.SMALL_TALK: 1.0,
            Intent.ESCALATE: 3.0
        }
        
        subject_multipliers = {
            Subject.MATH: 1.2,
            Subject.SCIENCE: 1.1,
            Subject.PROGRAMMING: 1.3,
            Subject.HISTORY: 1.0,
            Subject.LITERATURE: 1.0,
            Subject.GENERAL: 1.0
        }
        
        base_time = base_times.get(intent, 2.0)
        multiplier = subject_multipliers.get(subject, 1.0)
        
        return base_time * multiplier
    
    async def _analyze_context_for_intent(self, context: List[Dict[str, Any]]) -> Optional[Intent]:
        """Analyze context to provide intent hints"""
        try:
            if not context:
                return None
            
            # Look for recent intents in context
            recent_intents = []
            for entry in context[-5:]:  # Last 5 entries
                if entry.get('type') == 'intent':
                    recent_intents.append(entry.get('content'))
            
            # If recent context shows homework checking, likely more homework
            if any('homework' in intent.lower() for intent in recent_intents):
                return Intent.CHECK_HOMEWORK
            
            # If recent context shows quiz, likely more quiz
            if any('quiz' in intent.lower() for intent in recent_intents):
                return Intent.START_QUIZ
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing context for intent: {e}")
            return None
    
    async def _analyze_context_for_subject(self, context: List[Dict[str, Any]]) -> Optional[Subject]:
        """Analyze context to provide subject hints"""
        try:
            if not context:
                return None
            
            # Look for recent subjects in context
            recent_subjects = []
            for entry in context[-5:]:  # Last 5 entries
                if entry.get('type') == 'subject':
                    recent_subjects.append(entry.get('content'))
            
            # Count subject mentions
            subject_counts = {}
            for subject in recent_subjects:
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
            
            # Return most frequent subject
            if subject_counts:
                most_frequent = max(subject_counts, key=subject_counts.get)
                # Map string to Subject enum
                subject_mapping = {
                    'math': Subject.MATH,
                    'science': Subject.SCIENCE,
                    'programming': Subject.PROGRAMMING,
                    'history': Subject.HISTORY,
                    'literature': Subject.LITERATURE,
                    'general': Subject.GENERAL
                }
                return subject_mapping.get(most_frequent.lower())
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing context for subject: {e}")
            return None
    
    async def get_intent_patterns(self) -> Dict[str, any]:
        """Get all intent patterns for debugging"""
        return self.intent_patterns
    
    async def get_subject_patterns(self) -> Dict[str, any]:
        """Get all subject patterns for debugging"""
        return self.subject_patterns
    
    async def add_custom_pattern(self, intent: Intent, pattern: str, pattern_type: str = 'regex') -> bool:
        """Add custom pattern for intent classification"""
        try:
            if intent not in self.intent_patterns:
                return False
            
            if pattern_type == 'regex':
                self.intent_patterns[intent]['patterns'].append(pattern)
            elif pattern_type == 'keyword':
                self.intent_patterns[intent]['keywords'].append(pattern)
            
            logger.info(f"Added custom {pattern_type} pattern for {intent}: {pattern}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom pattern: {e}")
            return False