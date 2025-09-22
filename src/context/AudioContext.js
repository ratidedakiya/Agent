import React, { createContext, useContext, useState, useRef, useEffect } from 'react';

const AudioContext = createContext();

export const useAudio = () => {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error('useAudio must be used within an AudioProvider');
  }
  return context;
};

export const AudioProvider = ({ children }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [audioLevel, setAudioLevel] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  
  const audioRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    // Initialize audio context and analyser
    const initAudio = async () => {
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        analyserRef.current = analyser;
        
        // Start audio level monitoring
        startAudioLevelMonitoring();
      } catch (error) {
        console.error('Error initializing audio context:', error);
      }
    };

    initAudio();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const startAudioLevelMonitoring = () => {
    const monitor = () => {
      if (analyserRef.current) {
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        
        const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
        setAudioLevel(average / 255);
      }
      
      animationFrameRef.current = requestAnimationFrame(monitor);
    };
    
    monitor();
  };

  const playAudio = (audioData, options = {}) => {
    try {
      // Stop current audio if playing
      if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
      }

      // Create new audio element
      const audio = new Audio();
      
      if (typeof audioData === 'string') {
        audio.src = audioData;
      } else if (audioData instanceof Blob) {
        audio.src = URL.createObjectURL(audioData);
      } else if (audioData instanceof ArrayBuffer) {
        const blob = new Blob([audioData], { type: 'audio/wav' });
        audio.src = URL.createObjectURL(blob);
      } else {
        throw new Error('Invalid audio data format');
      }

      // Set audio properties
      audio.volume = isMuted ? 0 : volume;
      audio.loop = options.loop || false;
      audio.playbackRate = options.playbackRate || 1;

      // Event listeners
      audio.addEventListener('play', () => {
        setIsPlaying(true);
        setCurrentAudio(audio);
      });

      audio.addEventListener('pause', () => {
        setIsPlaying(false);
      });

      audio.addEventListener('ended', () => {
        setIsPlaying(false);
        setCurrentAudio(null);
      });

      audio.addEventListener('error', (e) => {
        console.error('Audio playback error:', e);
        setIsPlaying(false);
        setCurrentAudio(null);
      });

      // Play audio
      audio.play();
      
      return audio;
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
      setCurrentAudio(null);
    }
  };

  const pauseAudio = () => {
    if (currentAudio) {
      currentAudio.pause();
    }
  };

  const resumeAudio = () => {
    if (currentAudio) {
      currentAudio.play();
    }
  };

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      setCurrentAudio(null);
      setIsPlaying(false);
    }
  };

  const toggleMute = () => {
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    
    if (currentAudio) {
      currentAudio.volume = newMuted ? 0 : volume;
    }
  };

  const setAudioVolume = (newVolume) => {
    const clampedVolume = Math.max(0, Math.min(1, newVolume));
    setVolume(clampedVolume);
    
    if (currentAudio) {
      currentAudio.volume = isMuted ? 0 : clampedVolume;
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      });

      // Connect to analyser for level monitoring
      if (analyserRef.current) {
        const audioContext = analyserRef.current.context;
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyserRef.current);
      }

      setIsRecording(true);
      return stream;
    } catch (error) {
      console.error('Error starting recording:', error);
      throw error;
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
  };

  const getAudioLevel = () => {
    return audioLevel;
  };

  const isAudioSupported = () => {
    return !!(window.AudioContext || window.webkitAudioContext);
  };

  const isRecordingSupported = () => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  };

  const value = {
    // State
    isRecording,
    isPlaying,
    currentAudio,
    audioLevel,
    isMuted,
    volume,
    
    // Actions
    playAudio,
    pauseAudio,
    resumeAudio,
    stopAudio,
    toggleMute,
    setAudioVolume,
    startRecording,
    stopRecording,
    getAudioLevel,
    
    // Utilities
    isAudioSupported,
    isRecordingSupported,
  };

  return (
    <AudioContext.Provider value={value}>
      {children}
    </AudioContext.Provider>
  );
};