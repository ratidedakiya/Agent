import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import './App.css';

// Components
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import QuizInterface from './components/QuizInterface';
import HomeworkInterface from './components/HomeworkInterface';
import Settings from './components/Settings';
import SessionManager from './components/SessionManager';

// Context
import { SessionProvider } from './context/SessionContext';
import { AudioProvider } from './context/AudioContext';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState('chat');
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Initialize session on app load
    const initializeSession = async () => {
      try {
        const response = await fetch('/api/sessions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 'user_' + Date.now(),
            language: 'en',
            persona: 'friendly'
          }),
        });
        
        if (response.ok) {
          const sessionData = await response.json();
          setSession(sessionData);
        }
      } catch (error) {
        console.error('Failed to initialize session:', error);
      }
    };

    initializeSession();
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleViewChange = (view) => {
    setCurrentView(view);
    setSidebarOpen(false);
  };

  if (!session) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing AI Tutor...</p>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider value={{ session, setSession }}>
        <AudioProvider>
          <Router>
            <div className="min-h-screen bg-gray-50">
              <Header 
                onToggleSidebar={toggleSidebar}
                currentView={currentView}
                onViewChange={handleViewChange}
              />
              
              <div className="flex">
                <Sidebar 
                  isOpen={sidebarOpen}
                  onClose={() => setSidebarOpen(false)}
                  currentView={currentView}
                  onViewChange={handleViewChange}
                />
                
                <main className="flex-1 transition-all duration-300 ease-in-out">
                  <Routes>
                    <Route path="/" element={<Navigate to="/chat" replace />} />
                    <Route 
                      path="/chat" 
                      element={
                        <ChatInterface 
                          session={session}
                          onViewChange={handleViewChange}
                        />
                      } 
                    />
                    <Route 
                      path="/quiz" 
                      element={
                        <QuizInterface 
                          session={session}
                          onViewChange={handleViewChange}
                        />
                      } 
                    />
                    <Route 
                      path="/homework" 
                      element={
                        <HomeworkInterface 
                          session={session}
                          onViewChange={handleViewChange}
                        />
                      } 
                    />
                    <Route 
                      path="/settings" 
                      element={
                        <Settings 
                          session={session}
                          onViewChange={handleViewChange}
                        />
                      } 
                    />
                  </Routes>
                </main>
              </div>
              
              <Toaster 
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                }}
              />
            </div>
          </Router>
        </AudioProvider>
      </SessionProvider>
    </QueryClientProvider>
  );
}

export default App;