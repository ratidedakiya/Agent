import React from 'react';
import { 
  Menu, 
  X, 
  MessageCircle, 
  HelpCircle, 
  FileText, 
  Settings,
  Mic,
  MicOff,
  Volume2,
  VolumeX
} from 'lucide-react';

const Header = ({ onToggleSidebar, currentView, onViewChange }) => {
  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: MessageCircle, path: '/chat' },
    { id: 'quiz', label: 'Quiz', icon: HelpCircle, path: '/quiz' },
    { id: 'homework', label: 'Homework', icon: FileText, path: '/homework' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left side - Menu button and logo */}
          <div className="flex items-center space-x-4">
            <button
              onClick={onToggleSidebar}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 lg:hidden"
            >
              <Menu className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-3">
              <div className="avatar-container">
                <div className="w-full h-full flex items-center justify-center text-white font-bold text-lg">
                  AI
                </div>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Tutor</h1>
                <p className="text-sm text-gray-500">Your personal learning assistant</p>
              </div>
            </div>
          </div>

          {/* Center - Navigation tabs (hidden on mobile) */}
          <nav className="hidden lg:flex space-x-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => onViewChange(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right side - Audio controls and status */}
          <div className="flex items-center space-x-4">
            {/* Audio status indicator */}
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <Mic className="h-4 w-4 text-green-500" />
                <span className="text-xs text-gray-500">Listening</span>
              </div>
              <div className="flex items-center space-x-1">
                <Volume2 className="h-4 w-4 text-blue-500" />
                <span className="text-xs text-gray-500">Audio On</span>
              </div>
            </div>

            {/* Session status */}
            <div className="hidden sm:flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Session Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile navigation tabs */}
      <div className="lg:hidden border-t border-gray-200">
        <div className="flex overflow-x-auto">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors duration-200 ${
                  isActive
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};

export default Header;