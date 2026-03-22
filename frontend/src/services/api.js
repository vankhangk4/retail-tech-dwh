import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Request interceptor: add JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// Auth
export const login = (username, password) =>
  api.post('/api/auth/login/json', { username, password });

export const getMe = () =>
  api.get('/api/auth/me');

// Tenants
export const getTenants = () =>
  api.get('/api/admin/tenants');

export const createTenant = (data) =>
  api.post('/api/admin/tenants', data);

export const deleteTenant = (tenantId) =>
  api.delete(`/api/admin/tenants/${tenantId}`);

// Users
export const getUsers = () =>
  api.get('/api/admin/users');

export const createUser = (data) =>
  api.post('/api/admin/users', data);

export const updateUser = (userId, data) =>
  api.put(`/api/admin/users/${userId}`, data);

export const deleteUser = (userId) =>
  api.delete(`/api/admin/users/${userId}`);

export const getTenantUsers = () =>
  api.get('/api/tenant/users');

export const createTenantUser = (data) =>
  api.post('/api/tenant/users', data);

export const deleteTenantUser = (userId) =>
  api.delete(`/api/tenant/users/${userId}`);

// Stats
export const getStats = () =>
  api.get('/api/stats');

export const getSummary = () =>
  api.get('/api/stats/summary');

// ETL
export const triggerETL = () =>
  api.post('/api/etl/run');

export const getETLStatus = (runId) =>
  api.get(`/api/etl/status/${runId}`);

export const getETLHistory = () =>
  api.get('/api/etl/history');

// Upload
export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const listFiles = () =>
  api.get('/api/upload');

// Embed
export const getSupersetToken = () =>
  api.get('/api/embed/superset-token');

export default api;
