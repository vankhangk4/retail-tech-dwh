import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

// Main axios instance — all authenticated requests
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Separate instance for logout — never cancelled
const logoutClient = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Read persisted impersonation on init
const getImpersonatedTenant = () => localStorage.getItem('impersonated_tenant');

// Request interceptor: attach JWT token + impersonation header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const imp = getImpersonatedTenant();
  if (imp) {
    config.headers['X-Impersonate-Tenant'] = imp;
  }
  return config;
});

// Request interceptor for logout: attach token from argument (not localStorage, which may be cleared)
logoutClient.interceptors.request.use((config) => {
  return config;
});

// Response interceptor: handle 401 → clear auth and redirect to login
// Skip redirect for login endpoints so error messages display properly
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes('/login')) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// ─── Auth ───────────────────────────────────────────────────────────────────

export const apiLogin = (username, password) =>
  api.post('/api/auth/login/json', { username, password });

export const getMe = () =>
  api.get('/api/auth/me');

export const logout = (token) => {
  return logoutClient.post('/api/auth/logout', {}, {
    headers: { Authorization: `Bearer ${token}` },
  });
};

// ─── Tenants ────────────────────────────────────────────────────────────────

export const getTenants = () => api.get('/api/admin/tenants');
export const createTenant = (data) => api.post('/api/admin/tenants', data);
export const deleteTenant = (tenantId) => api.delete(`/api/admin/tenants/${tenantId}`);
export const getAdminStats = () => api.get('/api/admin/stats');

// ─── Users ──────────────────────────────────────────────────────────────────

export const getUsers = () => api.get('/api/admin/users');
export const createUser = (data) => api.post('/api/admin/users', data);
export const updateUser = (userId, data) => api.put(`/api/admin/users/${userId}`, data);
export const deleteUser = (userId) => api.delete(`/api/admin/users/${userId}`);

export const getTenantUsers = () => api.get('/api/tenant/users');
export const createTenantUser = (data) => api.post('/api/tenant/users', data);
export const deleteTenantUser = (userId) => api.delete(`/api/tenant/users/${userId}`);

// ─── Stats ──────────────────────────────────────────────────────────────────

export const getStats = () => api.get('/api/stats');
export const getSummary = () => api.get('/api/stats/summary');

// ─── ETL ─────────────────────────────────────────────────────────────────────

export const triggerETL = () => api.post('/api/etl/run');
export const getETLStatus = (runId) => api.get(`/api/etl/status/${runId}`);
export const getETLHistory = () => api.get('/api/etl/history');
export const getETLLogs = (runId) => api.get(`/api/etl/logs/${runId}`);

// ─── Upload ──────────────────────────────────────────────────────────────────

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const listFiles = () => api.get('/api/upload');

// ─── Embed ──────────────────────────────────────────────────────────────────

export const getSupersetToken = () => api.get('/api/embed/superset-token');
