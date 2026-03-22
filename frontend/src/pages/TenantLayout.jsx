import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: '📊', exact: true },
  { path: '/dashboard/etl', label: 'ETL Pipeline', icon: '⚙️' },
  { path: '/dashboard/upload', label: 'Upload Files', icon: '📁' },
  { path: '/dashboard/reports', label: 'Reports', icon: '📈' },
];

export default function TenantLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h2>User Portal</h2>
          <span>DATN Data Platform</span>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.exact}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <span style={{ marginRight: 10, fontSize: 18 }}>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-user">
          <div className="username">{user?.Username}</div>
          <div className="role">{user?.Role} · {user?.TenantId}</div>
          <button
            onClick={handleLogout}
            style={{ marginTop: 10, background: 'none', border: 'none', color: 'rgba(255,255,255,0.6)', cursor: 'pointer', fontSize: 13 }}
          >
            Đăng xuất
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
