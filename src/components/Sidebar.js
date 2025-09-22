import React from 'react';
import { 
  X, 
  MessageCircle, 
  HelpCircle, 
  FileText, 
  Settings,
  User,
  Clock,
  BookOpen,
  TrendingUp,
  Star,
  History,
  Download,
  Upload
} from 'lucide-react';

const Sidebar = ({ isOpen, onClose, currentView, onViewChange }) => {
  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: MessageCircle, path: '/chat' },
    { id: 'quiz', label: 'Quiz', icon: HelpCircle, path: '/quiz' },
    { id: 'homework', label: 'Homework', icon: FileText, path: '/homework' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
  ];

  const quickActions = [
    { id: 'new-session', label: 'New Session', icon: Clock },
    { id: 'study-plan', label: 'Study Plan', icon: BookOpen },
    { id: 'progress', label: 'Progress', icon: TrendingUp },
    { id: 'favorites', label: 'Favorites', icon: Star },
  ];

  const recentActivity = [
    { id: 1, type: 'question', text: 'What is photosynthesis?', time: '2 min ago' },
    { id: 2, type: 'quiz', text: 'Math Quiz - Algebra', time: '15 min ago' },
    { id: 3, type: 'homework', text: 'Science Homework Review', time: '1 hour ago' },
  ];

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="sidebar-overlay"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`sidebar ${isOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">AI Tutor</h2>
            <button
              onClick={onClose}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 lg:hidden"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            <div className="space-y-1">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                Main
              </h3>
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentView === item.id;
                
                return (
                  <button
                    key={item.id}
                    onClick={() => onViewChange(item.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                      isActive
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Quick Actions */}
            <div className="space-y-1 mt-8">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                Quick Actions
              </h3>
              {quickActions.map((action) => {
                const Icon = action.icon;
                
                return (
                  <button
                    key={action.id}
                    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors duration-200"
                  >
                    <Icon className="h-5 w-5" />
                    <span>{action.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Recent Activity */}
            <div className="space-y-1 mt-8">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                Recent Activity
              </h3>
              <div className="space-y-2">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
                  >
                    <div className="flex-shrink-0">
                      {activity.type === 'question' && (
                        <MessageCircle className="h-4 w-4 text-blue-500" />
                      )}
                      {activity.type === 'quiz' && (
                        <HelpCircle className="h-4 w-4 text-green-500" />
                      )}
                      {activity.type === 'homework' && (
                        <FileText className="h-4 w-4 text-purple-500" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 truncate">
                        {activity.text}
                      </p>
                      <p className="text-xs text-gray-500">
                        {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  Student User
                </p>
                <p className="text-xs text-gray-500">
                  Active Session
                </p>
              </div>
            </div>
            
            <div className="mt-4 flex space-x-2">
              <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-200">
                <Download className="h-3 w-3" />
                <span>Export</span>
              </button>
              <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-200">
                <Upload className="h-3 w-3" />
                <span>Import</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;