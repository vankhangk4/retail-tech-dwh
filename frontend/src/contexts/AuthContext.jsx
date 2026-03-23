import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getMe, logout as apiLogout } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // initializing = true means "checking stored token in background"
  // Set to true only when a token exists, so authenticated users see a brief
  // spinner while we validate, but unauthenticated users skip it entirely.
  const [initializing, setInitializing] = useState(
    () => !!localStorage.getItem('token')
  );

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem('token');
        setUser(null);
      })
      .finally(() => setInitializing(false));
  }, []);

  // Login: set user in context (React batches this)
  const login = useCallback((userData) => {
    setUser(userData);
    setInitializing(false);
  }, []);

  // Logout: clear everything
  const logout = useCallback(async () => {
    const token = localStorage.getItem('token');
    localStorage.removeItem('token');
    setUser(null);
    setInitializing(false);
    if (token) {
      try {
        await apiLogout(token);
      } catch {
        // ignore
      }
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, loading: initializing }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
