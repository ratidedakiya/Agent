import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Camera,
  Paperclip,
  Smile,
  MoreVertical,
  Play,
  Pause,
  Square
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import toast from 'react-hot-toast';
import AudioRecorder from './AudioRecorder';
import MessageBubble from './MessageBubble';
import AvatarVideo from './AvatarVideo';

const ChatInterface = ({ session, onViewChange }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [showAvatar, setShowAvatar] = useState(false);
  const [avatarVideo, setAvatarVideo] = useState(null);
  
  const messagesEndRef = useRef(null);
  const audioRef = useRef(null);
  const queryClient = useQueryClient();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Process text input
  const processTextMutation = useMutation(
    async (text) => {
      const response = await fetch('/api/text/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          session_id: session.session_id,
          language: session.language,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to process text');
      }

      return response.json();
    },
    {
      onSuccess: (data) => {
        // Add AI response to messages
        const aiMessage = {
          id: Date.now(),
          type: 'ai',
          text: data.text,
          summary: data.summary,
          confidence: data.confidence,
          need_steps: data.need_steps,
          citations: data.citations,
          voice_style: data.voice_style,
          emotion: data.emotion,
          gesture_tag: data.gesture_tag,
          emphasis_spans: data.emphasis_spans,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, aiMessage]);
        setIsTyping(false);

        // Show avatar if video is available
        if (data.video_url) {
          setAvatarVideo(data.video_url);
          setShowAvatar(true);
        }

        // Play audio if available
        if (data.audio_data) {
          playAudio(data.audio_data);
        }
      },
      onError: (error) => {
        console.error('Error processing text:', error);
        toast.error('Failed to process your message. Please try again.');
        setIsTyping(false);
      },
    }
  );

  // Process audio input
  const processAudioMutation = useMutation(
    async (audioBlob) => {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'audio.wav');
      formData.append('session_id', session.session_id);

      const response = await fetch('/api/audio/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process audio');
      }

      return response.json();
    },
    {
      onSuccess: (data) => {
        // Add user audio message
        const userMessage = {
          id: Date.now(),
          type: 'user',
          text: data.transcript,
          isAudio: true,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);

        // Process the transcript as text
        processTextMutation.mutate(data.transcript);
      },
      onError: (error) => {
        console.error('Error processing audio:', error);
        toast.error('Failed to process audio. Please try again.');
      },
    }
  );

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: inputText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    // Process the message
    processTextMutation.mutate(inputText);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleAudioRecorded = (audioBlob) => {
    processAudioMutation.mutate(audioBlob);
  };

  const playAudio = (audioData) => {
    if (currentAudio) {
      currentAudio.pause();
    }

    const audio = new Audio(`data:audio/wav;base64,${audioData}`);
    audio.addEventListener('ended', () => {
      setIsPlaying(false);
      setCurrentAudio(null);
    });

    audio.play();
    setCurrentAudio(audio);
    setIsPlaying(true);
  };

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
      setIsPlaying(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setShowAvatar(false);
    setAvatarVideo(null);
    stopAudio();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="avatar-container">
              <div className="w-full h-full flex items-center justify-center text-white font-bold text-lg">
                AI
              </div>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">AI Tutor Chat</h2>
              <p className="text-sm text-gray-500">
                {session?.persona || 'Friendly'} • {session?.language || 'English'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowAvatar(!showAvatar)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Toggle Avatar"
            >
              <Camera className="h-5 w-5" />
            </button>
            
            <button
              onClick={clearChat}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Clear Chat"
            >
              <MoreVertical className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Messages */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <span className="text-2xl font-bold text-white">AI</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Welcome to AI Tutor!
                </h3>
                <p className="text-gray-600 mb-6 max-w-md">
                  I'm here to help you learn. Ask me questions, request quizzes, or upload homework for review.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-md">
                  <button
                    onClick={() => setInputText("Explain photosynthesis")}
                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all duration-200"
                  >
                    <span className="text-sm font-medium text-gray-900">Ask a question</span>
                    <p className="text-xs text-gray-500 mt-1">Get explanations and help</p>
                  </button>
                  <button
                    onClick={() => onViewChange('quiz')}
                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all duration-200"
                  >
                    <span className="text-sm font-medium text-gray-900">Take a quiz</span>
                    <p className="text-xs text-gray-500 mt-1">Test your knowledge</p>
                  </button>
                  <button
                    onClick={() => onViewChange('homework')}
                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all duration-200"
                  >
                    <span className="text-sm font-medium text-gray-900">Upload homework</span>
                    <p className="text-xs text-gray-500 mt-1">Get feedback on your work</p>
                  </button>
                  <button
                    onClick={() => setInputText("Help me study for my math test")}
                    className="p-3 text-left bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all duration-200"
                  >
                    <span className="text-sm font-medium text-gray-900">Study help</span>
                    <p className="text-xs text-gray-500 mt-1">Get personalized assistance</p>
                  </button>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  onPlayAudio={playAudio}
                  isPlaying={isPlaying && currentAudio}
                />
              ))
            )}
            
            {isTyping && (
              <div className="flex items-center space-x-2 text-gray-500">
                <div className="typing-indicator">
                  <div className="typing-dot" style={{ animationDelay: '0s' }}></div>
                  <div className="typing-dot" style={{ animationDelay: '0.2s' }}></div>
                  <div className="typing-dot" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <span className="text-sm">AI is thinking...</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message or question..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={1}
                  style={{ minHeight: '40px', maxHeight: '120px' }}
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <AudioRecorder
                  onRecordingStart={() => setIsRecording(true)}
                  onRecordingStop={() => setIsRecording(false)}
                  onAudioRecorded={handleAudioRecorded}
                  disabled={processTextMutation.isLoading || processAudioMutation.isLoading}
                />
                
                <button
                  onClick={handleSendMessage}
                  disabled={!inputText.trim() || processTextMutation.isLoading || processAudioMutation.isLoading}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
            
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
              <div className="flex items-center space-x-4">
                <span>Press Enter to send</span>
                <span>Shift + Enter for new line</span>
              </div>
              
              <div className="flex items-center space-x-2">
                {isPlaying && (
                  <button
                    onClick={stopAudio}
                    className="flex items-center space-x-1 text-red-600 hover:text-red-700"
                  >
                    <Square className="h-3 w-3" />
                    <span>Stop Audio</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Avatar Panel */}
        {showAvatar && (
          <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">AI Avatar</h3>
              <p className="text-sm text-gray-500">Interactive learning companion</p>
            </div>
            
            <div className="flex-1 p-4">
              {avatarVideo ? (
                <AvatarVideo videoUrl={avatarVideo} />
              ) : (
                <div className="flex items-center justify-center h-full bg-gray-100 rounded-lg">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl font-bold text-white">AI</span>
                    </div>
                    <p className="text-gray-600">Avatar will appear here</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;