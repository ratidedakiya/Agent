import React, { createContext, useContext, useState, useEffect } from 'react';

const SessionContext = createContext();

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

export const SessionProvider = ({ children, value }) => {
  const [session, setSession] = useState(value?.session || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Update session when value changes
  useEffect(() => {
    if (value?.session) {
      setSession(value.session);
    }
  }, [value?.session]);

  const updateSession = async (updates) => {
    if (!session) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/sessions/${session.session_id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error('Failed to update session');
      }

      const updatedSession = await response.json();
      setSession(updatedSession);
    } catch (err) {
      setError(err.message);
      console.error('Error updating session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshSession = async () => {
    if (!session) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/sessions/${session.session_id}`);

      if (!response.ok) {
        throw new Error('Failed to fetch session');
      }

      const sessionData = await response.json();
      setSession(sessionData);
    } catch (err) {
      setError(err.message);
      console.error('Error refreshing session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewSession = async (sessionData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      });

      if (!response.ok) {
        throw new Error('Failed to create session');
      }

      const newSession = await response.json();
      setSession(newSession);
      return newSession;
    } catch (err) {
      setError(err.message);
      console.error('Error creating session:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearSession = () => {
    setSession(null);
    setError(null);
  };

  const value = {
    session,
    setSession,
    updateSession,
    refreshSession,
    createNewSession,
    clearSession,
    isLoading,
    error,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};