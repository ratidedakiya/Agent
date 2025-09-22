import React, { useState } from 'react';
import { 
  User, 
  Volume2, 
  Monitor, 
  Globe, 
  Palette, 
  Save,
  RotateCcw,
  Mic,
  MicOff,
  Camera,
  CameraOff
} from 'lucide-react';

const Settings = ({ session, onViewChange }) => {
  const [settings, setSettings] = useState({
    // User preferences
    name: 'Student User',
    language: session?.language || 'en',
    persona: session?.persona || 'friendly',
    
    // Audio settings
    voiceStyle: 'friendly_male',
    volume: 1.0,
    speed: 1.0,
    pitch: 1.0,
    autoPlay: true,
    
    // Visual settings
    theme: 'light',
    avatarEnabled: true,
    gesturesEnabled: true,
    animationsEnabled: true,
    
    // Privacy settings
    dataCollection: true,
    analytics: true,
    feedback: true,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setHasChanges(true);
  };

  const saveSettings = async () => {
    setIsSaving(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update session with new settings
      if (session) {
        // This would typically update the session via API
        console.log('Saving settings:', settings);
      }
      
      setHasChanges(false);
      // Show success message
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const resetSettings = () => {
    setSettings({
      name: 'Student User',
      language: 'en',
      persona: 'friendly',
      voiceStyle: 'friendly_male',
      volume: 1.0,
      speed: 1.0,
      pitch: 1.0,
      autoPlay: true,
      theme: 'light',
      avatarEnabled: true,
      gesturesEnabled: true,
      animationsEnabled: true,
      dataCollection: true,
      analytics: true,
      feedback: true,
    });
    setHasChanges(true);
  };

  const SettingSection = ({ title, icon: Icon, children }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Icon className="h-6 w-6 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      </div>
      {children}
    </div>
  );

  const SettingRow = ({ label, description, children }) => (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
      <div className="flex-1">
        <label className="text-sm font-medium text-gray-900">{label}</label>
        {description && (
          <p className="text-sm text-gray-500 mt-1">{description}</p>
        )}
      </div>
      <div className="ml-4">
        {children}
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Customize your AI Tutor experience</p>
        </div>
        
        <div className="flex items-center space-x-3">
          {hasChanges && (
            <button
              onClick={resetSettings}
              className="btn-secondary"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </button>
          )}
          <button
            onClick={saveSettings}
            disabled={!hasChanges || isSaving}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* User Profile */}
        <SettingSection title="User Profile" icon={User}>
          <SettingRow label="Name" description="Your display name">
            <input
              type="text"
              value={settings.name}
              onChange={(e) => handleSettingChange('name', e.target.value)}
              className="input-field w-48"
            />
          </SettingRow>
          
          <SettingRow label="Language" description="Preferred language for responses">
            <select
              value={settings.language}
              onChange={(e) => handleSettingChange('language', e.target.value)}
              className="input-field w-48"
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="gu">Gujarati</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
            </select>
          </SettingRow>
          
          <SettingRow label="Persona" description="AI tutor personality">
            <select
              value={settings.persona}
              onChange={(e) => handleSettingChange('persona', e.target.value)}
              className="input-field w-48"
            >
              <option value="friendly">Friendly</option>
              <option value="professional">Professional</option>
              <option value="encouraging">Encouraging</option>
              <option value="strict">Strict</option>
            </select>
          </SettingRow>
        </SettingSection>

        {/* Audio Settings */}
        <SettingSection title="Audio Settings" icon={Volume2}>
          <SettingRow label="Voice Style" description="Choose your preferred voice">
            <select
              value={settings.voiceStyle}
              onChange={(e) => handleSettingChange('voiceStyle', e.target.value)}
              className="input-field w-48"
            >
              <option value="friendly_male">Friendly Male</option>
              <option value="friendly_female">Friendly Female</option>
              <option value="professional_male">Professional Male</option>
              <option value="professional_female">Professional Female</option>
              <option value="encouraging_male">Encouraging Male</option>
              <option value="encouraging_female">Encouraging Female</option>
            </select>
          </SettingRow>
          
          <SettingRow label="Volume" description="Audio volume level">
            <div className="flex items-center space-x-3 w-48">
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.volume}
                onChange={(e) => handleSettingChange('volume', parseFloat(e.target.value))}
                className="flex-1"
              />
              <span className="text-sm text-gray-600 w-12">
                {Math.round(settings.volume * 100)}%
              </span>
            </div>
          </SettingRow>
          
          <SettingRow label="Speed" description="Speech playback speed">
            <div className="flex items-center space-x-3 w-48">
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={settings.speed}
                onChange={(e) => handleSettingChange('speed', parseFloat(e.target.value))}
                className="flex-1"
              />
              <span className="text-sm text-gray-600 w-12">
                {settings.speed}x
              </span>
            </div>
          </SettingRow>
          
          <SettingRow label="Auto-play Audio" description="Automatically play AI responses">
            <input
              type="checkbox"
              checked={settings.autoPlay}
              onChange={(e) => handleSettingChange('autoPlay', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </SettingRow>
        </SettingSection>

        {/* Visual Settings */}
        <SettingSection title="Visual Settings" icon={Monitor}>
          <SettingRow label="Theme" description="Choose your preferred theme">
            <select
              value={settings.theme}
              onChange={(e) => handleSettingChange('theme', e.target.value)}
              className="input-field w-48"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </SettingRow>
          
          <SettingRow label="Avatar Enabled" description="Show AI avatar during conversations">
            <input
              type="checkbox"
              checked={settings.avatarEnabled}
              onChange={(e) => handleSettingChange('avatarEnabled', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </SettingRow>
          
          <SettingRow label="Gestures Enabled" description="Show gesture animations">
            <input
              type="checkbox"
              checked={settings.gesturesEnabled}
              onChange={(e) => handleSettingChange('gesturesEnabled', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </SettingRow>
          
          <SettingRow label="Animations Enabled" description="Enable smooth animations">
            <input
              type="checkbox"
              checked={settings.animationsEnabled}
              onChange={(e) => handleSettingChange('animationsEnabled', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </SettingRow>
        </SettingSection>

        {/* Privacy Settings */}
        <SettingSection title="Privacy & Data" icon={Globe}>
          <SettingRow label="Data Collection" description="Allow collection of usage data to improve the service">
            <input
              type="checkbox"
              checked={settings.dataCollection}
              onChange={(e) => handleSettingChange('dataCollection', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </SettingRow>
          
          <SettingRow label="Analytics" description="Help us improve by sharing anonymous usage statistics">
            <input
              type="checkbox"
              checked={settings.analytics}
              onChange={(e) => handleSettingChange('analytics', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </SettingRow>
          
          <SettingRow label="Feedback Collection" description="Allow collection of feedback to improve responses">
            <input
              type="checkbox"
              checked={settings.feedback}
              onChange={(e) => handleSettingChange('feedback', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </SettingRow>
        </SettingSection>

        {/* Session Info */}
        <SettingSection title="Session Information" icon={User}>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2">
              <span className="text-sm font-medium text-gray-900">Session ID</span>
              <span className="text-sm text-gray-600 font-mono">
                {session?.session_id || 'N/A'}
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm font-medium text-gray-900">Created</span>
              <span className="text-sm text-gray-600">
                {session?.created_at ? new Date(session.created_at).toLocaleString() : 'N/A'}
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm font-medium text-gray-900">Status</span>
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Active
              </span>
            </div>
          </div>
        </SettingSection>
      </div>

      <div className="mt-8 text-center">
        <button
          onClick={() => onViewChange('chat')}
          className="btn-secondary"
        >
          Back to Chat
        </button>
      </div>
    </div>
  );
};

export default Settings;