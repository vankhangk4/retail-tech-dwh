import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import AdminLayout from './pages/AdminLayout';
import TenantLayout from './pages/TenantLayout';
import DashboardPage from './pages/DashboardPage';
import TenantsPage from './pages/TenantsPage';
import UsersPage from './pages/UsersPage';
import TenantUsersPage from './pages/TenantUsersPage';
import ETLPage from './pages/ETLPage';
import UploadPage from './pages/UploadPage';
import ReportsPage from './pages/ReportsPage';

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        Đang tải...
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.Role)) return <Navigate to="/" replace />;

  return children;
}

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        Đang tải...
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={
        user ? <Navigate to={user.Role === 'SuperAdmin' ? '/admin' : '/dashboard'} replace /> : <LoginPage />
      } />

      {/* SuperAdmin routes */}
      <Route path="/admin" element={
        <ProtectedRoute roles={['SuperAdmin']}>
          <AdminLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="tenants" replace />} />
        <Route path="tenants" element={<TenantsPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="etl" element={<ETLPage />} />
      </Route>

      {/* TenantAdmin & User routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <TenantLayout />
        </ProtectedRoute>
      }>
        <Route index element={<DashboardPage />} />
        <Route path="etl" element={<ETLPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="reports" element={<ReportsPage />} />
      </Route>

      <Route path="/" element={
        <Navigate to={user ? (user.Role === 'SuperAdmin' ? '/admin' : '/dashboard') : '/login'} replace />
      } />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
