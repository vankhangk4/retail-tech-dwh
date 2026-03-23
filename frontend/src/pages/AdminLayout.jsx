import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Building2,
  Users,
  RefreshCw,
  LogOut,
  Menu,
  Database,
  ChevronRight,
  Shield,
} from 'lucide-react';

const navItems = [
  { path: '/admin/tenants', label: 'Quản lý Tenant', icon: Building2 },
  { path: '/admin/users', label: 'Quản lý Users', icon: Users },
  { path: '/admin/etl', label: 'ETL History', icon: RefreshCw },
];

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const closeSidebar = () => setSidebarOpen(false);

  const getInitials = (name) => {
    if (!name) return 'SA';
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="layout">
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={closeSidebar}
      />

      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="logo-icon">
            <Shield size={20} color="white" />
          </div>
          <h2>Admin Portal</h2>
          <span>SuperAdmin</span>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => isActive ? 'active' : ''}
                onClick={closeSidebar}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">
            <div className="avatar">{getInitials(user?.Username)}</div>
            <div style={{ minWidth: 0 }}>
              <div className="username">{user?.Username}</div>
              <div className="role">
                {user?.Role} <ChevronRight size={10} style={{ verticalAlign: 'middle' }} />
              </div>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={14} />
            Đăng xuất
          </button>
        </div>
      </aside>

      <main className="main-content">
        <div className="mobile-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 32, height: 32, background: 'linear-gradient(135deg, #1e3c72, #3b82f6)',
              borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Shield size={16} color="white" />
            </div>
            <h2>Admin Portal</h2>
          </div>
          <button className="mobile-menu-btn" onClick={() => setSidebarOpen(true)}>
            <Menu size={20} />
          </button>
        </div>

        <Outlet />
      </main>
    </div>
  );
}
