import React, { useState, useEffect } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Building2,
  Users,
  RefreshCw,
  LogOut,
  Menu,
  ChevronRight,
  Shield,
  Eye,
  X,
  ChevronDown,
  TrendingUp,
} from 'lucide-react';

const navItems = [
  { path: '/admin', label: 'Dashboard', icon: TrendingUp, exact: true },
  { path: '/admin/tenants', label: 'Quản lý Tenant', icon: Building2 },
  { path: '/admin/users', label: 'Quản lý Users', icon: Users },
  { path: '/admin/etl', label: 'ETL History', icon: RefreshCw },
];

export default function AdminLayout() {
  const { user, logout, impersonatedTenant, impersonateTenant, stopImpersonation, tenants, tenantsLoading, loadTenants } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showImpDropdown, setShowImpDropdown] = useState(false);

  useEffect(() => {
    if (user?.Role === 'SuperAdmin') {
      loadTenants();
    }
  }, [user?.Role]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = () => setShowImpDropdown(false);
    if (showImpDropdown) document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [showImpDropdown]);

  const handleImpersonate = (tenant) => {
    impersonateTenant(tenant.TenantId);
    setShowImpDropdown(false);
    // Trigger a re-render of DashboardPage by navigating to it
    window.location.href = '/dashboard';
  };

  const handleStopImpersonate = () => {
    stopImpersonation();
    window.location.href = '/admin/tenants';
  };

  const handleLogout = () => {
    logout();
    // ProtectedRoute handles redirect when user becomes null
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
                end={item.exact}
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
          {/* Impersonation badge / dropdown */}
          {impersonatedTenant ? (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: '#fef3c7', border: '1px solid #fcd34d',
              borderRadius: 8, padding: '6px 10px', marginBottom: 10,
            }}>
              <Eye size={13} style={{ color: '#d97706', flexShrink: 0 }} />
              <span style={{ fontSize: 11, fontWeight: 600, color: '#92400e', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {impersonatedTenant}
              </span>
              <button
                onClick={handleStopImpersonate}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  padding: 0, display: 'flex', alignItems: 'center',
                  color: '#d97706', flexShrink: 0,
                }}
                title="Dừng impersonate"
              >
                <X size={13} />
              </button>
            </div>
          ) : (
            <div
              style={{ position: 'relative', marginBottom: 10 }}
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setShowImpDropdown(!showImpDropdown)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  width: '100%', background: '#eff6ff',
                  border: '1px solid #bfdbfe', borderRadius: 8,
                  padding: '6px 10px', cursor: 'pointer',
                  fontSize: 12, color: '#1d4ed8', fontWeight: 500,
                  textAlign: 'left',
                }}
              >
                <Eye size={13} style={{ flexShrink: 0 }} />
                <span style={{ flex: 1 }}>Xem như tenant...</span>
                <ChevronDown size={12} />
              </button>
              {showImpDropdown && (
                <div style={{
                  position: 'absolute', bottom: '100%', left: 0, right: 0,
                  background: '#fff', border: '1px solid #e2e8f0',
                  borderRadius: 8, boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                  maxHeight: 200, overflowY: 'auto', zIndex: 100,
                  marginBottom: 4,
                }}>
                  {tenantsLoading ? (
                    <>
                      {[1, 2, 3].map((i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px' }}>
                          <div className="skeleton" style={{ width: 12, height: 12, borderRadius: 2 }} />
                          <div className="skeleton" style={{ width: 60, height: 12 }} />
                          <div className="skeleton" style={{ width: 80, height: 10 }} />
                        </div>
                      ))}
                    </>
                  ) : tenants.length === 0 ? (
                    <div style={{ padding: '10px 12px', color: '#94a3b8', fontSize: 12 }}>Không có tenant</div>
                  ) : tenants.map((t) => (
                    <button
                      key={t.TenantId}
                      onClick={() => handleImpersonate(t)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 8,
                        width: '100%', padding: '8px 12px',
                        background: 'none', border: 'none', cursor: 'pointer',
                        textAlign: 'left', fontSize: 12, color: '#1e293b',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
                    >
                      <Building2 size={12} style={{ color: '#64748b', flexShrink: 0 }} />
                      <span style={{ fontWeight: 500 }}>{t.TenantId}</span>
                      <span style={{ color: '#94a3b8', fontSize: 11 }}>{t.TenantName}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

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
