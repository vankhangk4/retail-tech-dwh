import React, { useState, useEffect } from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getTenants } from '../services/api';
import {
  LayoutDashboard,
  RefreshCw,
  Upload,
  BarChart3,
  LogOut,
  Menu,
  Database,
  ChevronRight,
  Eye,
  X,
  ChevronDown,
  Building2,
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, exact: true },
  { path: '/dashboard/etl', label: 'ETL Pipeline', icon: RefreshCw },
  { path: '/dashboard/upload', label: 'Upload Files', icon: Upload },
  { path: '/dashboard/reports', label: 'Reports', icon: BarChart3 },
];

export default function TenantLayout() {
  const { user, logout, impersonatedTenant, impersonateTenant, stopImpersonation } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showImpDropdown, setShowImpDropdown] = useState(false);
  const [tenants, setTenants] = useState([]);
  const [loadingTenants, setLoadingTenants] = useState(false);

  const isSuperAdmin = user?.Role === 'SuperAdmin';

  useEffect(() => {
    if (isSuperAdmin) loadTenants();
  }, [isSuperAdmin]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = () => setShowImpDropdown(false);
    if (showImpDropdown) document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [showImpDropdown]);

  const loadTenants = async () => {
    setLoadingTenants(true);
    try {
      const res = await getTenants();
      setTenants(res.data);
    } catch {
      // ignore
    } finally {
      setLoadingTenants(false);
    }
  };

  const handleImpersonate = (tenant) => {
    impersonateTenant(tenant.TenantId);
    setShowImpDropdown(false);
    // Force reload to pick up new header
    window.location.reload();
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
    if (!name) return 'U';
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="layout">
      {/* Sidebar overlay for mobile */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={closeSidebar}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="logo-icon">
            <Database size={20} color="white" />
          </div>
          <h2>DATN Platform</h2>
          <span>Data Warehouse</span>
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

          {/* SuperAdmin nav back to admin */}
          {isSuperAdmin && (
            <NavLink
              to="/admin/tenants"
              className={({ isActive }) => isActive ? 'active' : ''}
              onClick={closeSidebar}
              style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid rgba(255,255,255,0.1)' }}
            >
              <Database size={18} />
              <span>Quản trị</span>
            </NavLink>
          )}
        </nav>

        <div className="sidebar-user">
          {/* Impersonation controls — only for SuperAdmin */}
          {isSuperAdmin && (
            impersonatedTenant ? (
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
                    {loadingTenants ? (
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
            )
          )}

          <div className="user-avatar">
            <div className="avatar">{getInitials(user?.Username)}</div>
            <div style={{ minWidth: 0 }}>
              <div className="username">{user?.Username}</div>
              <div className="role">
                {user?.Role} <ChevronRight size={10} style={{ verticalAlign: 'middle' }} /> {user?.TenantId}
              </div>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <LogOut size={14} />
            Đăng xuất
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        {/* Mobile header */}
        <div className="mobile-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 32, height: 32, background: 'linear-gradient(135deg, #1e3c72, #3b82f6)',
              borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <Database size={16} color="white" />
            </div>
            <h2>DATN Platform</h2>
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
