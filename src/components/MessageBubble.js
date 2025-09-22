import React, { useState } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Copy, 
  ThumbsUp, 
  ThumbsDown,
  ExternalLink,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const MessageBubble = ({ message, onPlayAudio, isPlaying }) => {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const isUser = message.type === 'user';
  const isAI = message.type === 'ai';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    toast.success('Copied to clipboard');
  };

  const handleFeedback = (type) => {
    setFeedback(type);
    setShowFeedback(false);
    toast.success(`Feedback submitted: ${type === 'positive' ? '👍' : '👎'}`);
  };

  const getGestureColor = (gesture) => {
    const colors = {
      'affirmative': 'gesture-affirmative',
      'corrective': 'gesture-corrective',
      'illustrative': 'gesture-illustrative',
      'questioning': 'gesture-questioning',
      'pointing': 'gesture-pointing'
    };
    return colors[gesture] || 'gesture-affirmative';
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      'calm': 'emotion-calm',
      'encouraging': 'emotion-encouraging',
      'corrective': 'emotion-corrective',
      'excited': 'emotion-excited',
      'neutral': 'emotion-neutral'
    };
    return colors[emotion] || 'emotion-neutral';
  };

  const renderEmphasisSpans = (text, emphasisSpans) => {
    if (!emphasisSpans || emphasisSpans.length === 0) {
      return text;
    }

    let result = text;
    let offset = 0;

    // Sort spans by start position
    const sortedSpans = [...emphasisSpans].sort((a, b) => a.start - b.start);

    sortedSpans.forEach((span, index) => {
      const adjustedStart = span.start + offset;
      const adjustedEnd = span.end + offset;
      
      if (adjustedStart >= 0 && adjustedEnd <= result.length) {
        const before = result.substring(0, adjustedStart);
        const emphasized = result.substring(adjustedStart, adjustedEnd);
        const after = result.substring(adjustedEnd);
        
        result = `${before}<strong>${emphasized}</strong>${after}`;
        offset += 17; // Length of <strong></strong> tags
      }
    });

    return result;
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start space-x-3 max-w-xs lg:max-w-md ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          {isUser ? (
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">U</span>
            </div>
          ) : (
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-bold">AI</span>
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`message-bubble ${isUser ? 'message-user' : 'message-ai'}`}>
            {/* Message Text */}
            <div className="mb-2">
              {isAI && message.emphasis_spans ? (
                <div 
                  dangerouslySetInnerHTML={{ 
                    __html: renderEmphasisSpans(message.text, message.emphasis_spans) 
                  }}
                />
              ) : (
                <p className="whitespace-pre-wrap">{message.text}</p>
              )}
            </div>

            {/* AI-specific metadata */}
            {isAI && (
              <div className="space-y-2">
                {/* Confidence and Steps indicators */}
                <div className="flex items-center space-x-2 text-xs">
                  {message.confidence && (
                    <div className="flex items-center space-x-1">
                      <div className={`w-2 h-2 rounded-full ${
                        message.confidence > 0.8 ? 'bg-green-500' : 
                        message.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}></div>
                      <span className="text-gray-500">
                        {Math.round(message.confidence * 100)}% confident
                      </span>
                    </div>
                  )}
                  
                  {message.need_steps && (
                    <div className="flex items-center space-x-1 text-blue-600">
                      <CheckCircle className="h-3 w-3" />
                      <span>Step-by-step</span>
                    </div>
                  )}
                </div>

                {/* Gesture and Emotion indicators */}
                <div className="flex items-center space-x-2">
                  {message.gesture_tag && (
                    <span className={`gesture-indicator ${getGestureColor(message.gesture_tag)}`}>
                      {message.gesture_tag.replace('_', ' ')}
                    </span>
                  )}
                  
                  {message.emotion && (
                    <span className={`emotion-indicator ${getEmotionColor(message.emotion)}`}>
                      {message.emotion}
                    </span>
                  )}
                </div>

                {/* Citations */}
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-500 mb-1">Sources:</p>
                    <div className="space-y-1">
                      {message.citations.map((citation, index) => (
                        <div key={index} className="flex items-center space-x-1 text-xs text-blue-600">
                          <ExternalLink className="h-3 w-3" />
                          <span>{citation}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Summary */}
                {message.summary && (
                  <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                    <strong>Summary:</strong> {message.summary}
                  </div>
                )}
              </div>
            )}

            {/* Audio controls for AI messages */}
            {isAI && message.audio_data && (
              <div className="mt-3 flex items-center space-x-2">
                <button
                  onClick={() => onPlayAudio(message.audio_data)}
                  className="flex items-center space-x-1 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors duration-200"
                >
                  {isPlaying ? (
                    <>
                      <Pause className="h-3 w-3" />
                      <span>Pause</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-3 w-3" />
                      <span>Play Audio</span>
                    </>
                  )}
                </button>
                
                <div className="flex items-center space-x-1 text-xs text-gray-500">
                  <Volume2 className="h-3 w-3" />
                  <span>Audio available</span>
                </div>
              </div>
            )}
          </div>

          {/* Message Actions */}
          <div className={`flex items-center space-x-2 mt-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <span className="text-xs text-gray-500">
              {message.timestamp?.toLocaleTimeString()}
            </span>
            
            {isAI && (
              <div className="flex items-center space-x-1">
                <button
                  onClick={handleCopy}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                  title="Copy message"
                >
                  <Copy className="h-3 w-3" />
                </button>
                
                <div className="relative">
                  <button
                    onClick={() => setShowFeedback(!showFeedback)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                    title="Provide feedback"
                  >
                    {feedback === 'positive' ? (
                      <ThumbsUp className="h-3 w-3 text-green-600" />
                    ) : feedback === 'negative' ? (
                      <ThumbsDown className="h-3 w-3 text-red-600" />
                    ) : (
                      <ThumbsUp className="h-3 w-3" />
                    )}
                  </button>
                  
                  {showFeedback && (
                    <div className="absolute top-0 left-0 mt-6 bg-white border border-gray-200 rounded-lg shadow-lg p-2 z-10">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleFeedback('positive')}
                          className="p-1 text-green-600 hover:bg-green-50 rounded transition-colors duration-200"
                          title="Good response"
                        >
                          <ThumbsUp className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleFeedback('negative')}
                          className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors duration-200"
                          title="Needs improvement"
                        >
                          <ThumbsDown className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;