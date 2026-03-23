import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getMe, logout as apiLogout, getTenants } from '../services/api';

const IMPERSONATE_KEY = 'impersonated_tenant';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // initializing = true means "checking stored token in background"
  // Set to true only when a token exists, so authenticated users see a brief
  // spinner while we validate, but unauthenticated users skip it entirely.
  const [initializing, setInitializing] = useState(
    () => !!localStorage.getItem('token')
  );

  // Sync impersonation with localStorage
  const [impersonatedTenant, setImpersonatedTenant] = useState(
    () => localStorage.getItem(IMPERSONATE_KEY)
  );

  // Cached tenant list — shared across AdminLayout and TenantsPage to avoid duplicate API calls
  const [tenants, setTenants] = useState([]);
  const [tenantsLoading, setTenantsLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem('token');
        localStorage.removeItem(IMPERSONATE_KEY);
        setUser(null);
        setImpersonatedTenant(null);
      })
      .finally(() => setInitializing(false));
  }, []);

  // Called when SuperAdmin selects a tenant to impersonate
  const impersonateTenant = useCallback((tenant) => {
    setImpersonatedTenant(tenant);
    localStorage.setItem(IMPERSONATE_KEY, tenant);
  }, []);

  // Clear impersonation
  const stopImpersonation = useCallback(() => {
    setImpersonatedTenant(null);
    localStorage.removeItem(IMPERSONATE_KEY);
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
    localStorage.removeItem(IMPERSONATE_KEY);
    setUser(null);
    setImpersonatedTenant(null);
    setTenants([]);
    setInitializing(false);
    if (token) {
      try {
        await apiLogout(token);
      } catch {
        // ignore
      }
    }
  }, []);

  // Load tenants — called by consumers that need fresh data
  const loadTenants = useCallback(async (force = false) => {
    if (!force && tenants.length > 0) return; // already loaded
    if (tenantsLoading) return; // already loading
    setTenantsLoading(true);
    try {
      const res = await getTenants();
      setTenants(res.data);
    } catch {
      // ignore
    } finally {
      setTenantsLoading(false);
    }
  }, [tenants.length, tenantsLoading]);

  return (
    <AuthContext.Provider value={{
      user, login, logout,
      loading: initializing,
      impersonatedTenant, impersonateTenant, stopImpersonation,
      tenants, tenantsLoading, loadTenants,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
