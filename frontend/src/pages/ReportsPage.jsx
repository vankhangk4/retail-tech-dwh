import React, { useEffect, useRef, useState } from 'react';
import { getSupersetToken } from '../services/api';
import { embedDashboard } from '@superset-ui/embedded-sdk';
import {
  BarChart3,
  ExternalLink,
  RefreshCw,
  AlertCircle,
  BookOpen,
} from 'lucide-react';

export default function ReportsPage() {
  const [token, setToken] = useState(null);
  const [dashboardId, setDashboardId] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [supersetUrl, setSupersetUrl] = useState('');
  const [iframeTs, setIframeTs] = useState(Date.now());
  const lastHandledEtlTsRef = useRef(0);
  const containerRef = useRef(null);

  useEffect(() => {
    if (token && containerRef.current && dashboardId && supersetUrl) {
      containerRef.current.innerHTML = '';
      embedDashboard({
        id: dashboardId,
        supersetDomain: supersetUrl,
        mountPoint: containerRef.current,
        fetchGuestToken: () => Promise.resolve(token),
        dashboardUiConfig: {
          hideTitle: true,
          hideChartControls: true,
          hideTab: true,
        },
      });
    }
  }, [token, dashboardId, supersetUrl, iframeTs]);

  const openSuperset = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await getSupersetToken();
      setToken(res.data.token);
      if (res.data.dashboard_id) setDashboardId(res.data.dashboard_id);
      if (res.data.superset_url) setSupersetUrl(res.data.superset_url);
      setIframeTs(Date.now());
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể lấy Superset token');
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    setToken(null);
    setLoading(true);
    try {
      const res = await getSupersetToken();
      setToken(res.data.token);
      if (res.data.dashboard_id) setDashboardId(res.data.dashboard_id);
      if (res.data.superset_url) setSupersetUrl(res.data.superset_url);
      setIframeTs(Date.now());
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể lấy Superset token');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleEtlSuccess = async () => {
      const rawTs = localStorage.getItem('last_etl_success_at');
      const ts = Number(rawTs || 0);
      if (!ts || ts <= lastHandledEtlTsRef.current) return;

      lastHandledEtlTsRef.current = ts;
      if (!token) return;

      setLoading(true);
      try {
        const res = await getSupersetToken();
        setToken(res.data.token);
        if (res.data.dashboard_id) setDashboardId(res.data.dashboard_id);
        if (res.data.superset_url) setSupersetUrl(res.data.superset_url);
        setIframeTs(Date.now());
      } catch {
        // silent auto-refresh failure, user can still refresh manually
      } finally {
        setLoading(false);
      }
    };

    const handleStorage = (e) => {
      if (e.key === 'last_etl_success_at' && e.newValue) {
        handleEtlSuccess();
      }
    };

    window.addEventListener('etl-success', handleEtlSuccess);
    window.addEventListener('storage', handleStorage);

    return () => {
      window.removeEventListener('etl-success', handleEtlSuccess);
      window.removeEventListener('storage', handleStorage);
    };
  }, [token]);

  return (
    <div>
      <div className="page-header">
        <h1>
          <BarChart3 size={24} style={{ color: '#3b82f6' }} />
          Reports & Dashboards
        </h1>
        <p>Xem báo cáo trực quan hóa dữ liệu trên Superset</p>
      </div>

      {/* Superset embed */}
      <div className="card" style={{ animationDelay: '0ms' }}>
        <div className="card-header">
          <h3>
            <BarChart3 size={16} />
            Apache Superset
          </h3>
          {!token ? (
            <button
              className="btn btn-primary btn-sm"
              onClick={openSuperset}
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2, marginRight: 4 }}></div>
                  Đang kết nối...
                </>
              ) : (
                <>
                  <ExternalLink size={16} />
                  Mở Dashboard
                </>
              )}
            </button>
          ) : (
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                className="btn btn-secondary btn-sm"
                onClick={refreshToken}
                disabled={loading}
              >
                <RefreshCw size={14} />
                Làm mới
              </button>
              <a
                href={`${supersetUrl}/superset/dashboard/p/${dashboardId}/`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-secondary btn-sm"
              >
                <ExternalLink size={14} />
                Mở trong tab mới
              </a>
            </div>
          )}
        </div>

        {error && (
          <div className="card-body">
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, padding: '16px 20px', background: '#fef2f2', borderRadius: 10, border: '1px solid #fecaca' }}>
              <AlertCircle size={20} style={{ color: '#dc2626', flexShrink: 0, marginTop: 1 }} />
              <div>
                <p style={{ fontWeight: 600, color: '#dc2626', marginBottom: 4 }}>Không thể kết nối Superset</p>
                <p style={{ fontSize: 13, color: '#64748b' }}>{error}</p>
                <p style={{ fontSize: 13, color: '#64748b', marginTop: 8 }}>
                  Đảm bảo Superset đang chạy tại <code style={{ background: '#fee2e2', padding: '1px 6px', borderRadius: 4, color: '#dc2626' }}>{supersetUrl || 'URL từ backend'}</code>
                </p>
              </div>
            </div>
          </div>
        )}

        {!token && !error && (
          <div className="card-body">
            {loading ? (
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                padding: '40px 20px',
              }}>
                <div style={{ textAlign: 'center' }}>
                  <div className="skeleton" style={{ width: 56, height: 56, borderRadius: 12, margin: '0 auto 12px' }} />
                  <div className="skeleton" style={{ width: 200, height: 14, margin: '0 auto 8px' }} />
                  <div className="skeleton" style={{ width: 280, height: 10, margin: '0 auto' }} />
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <BarChart3 size={56} style={{ color: '#cbd5e1' }} />
                <p style={{ marginTop: 14, fontWeight: 600, fontSize: 15, color: '#334155' }}>
                  Kết nối Superset Dashboard
                </p>
                <p style={{ marginTop: 6, fontSize: 13, color: '#94a3b8', maxWidth: 380, margin: '6px auto 0' }}>
                  Nhấn "Mở Dashboard" để truy cập báo cáo trực quan từ Superset.
                  <br />Đảm bảo Superset đang chạy tại <strong>{supersetUrl || 'URL từ backend'}</strong>
                </p>
              </div>
            )}
          </div>
        )}

        {token && (
          <div>
            <div className="superset-header">
              <BarChart3 size={18} />
              <h3>Superset Dashboard</h3>
            </div>
            <div 
              ref={containerRef} 
              className="superset-iframe" 
              style={{ width: '100%', minHeight: '800px', border: 'none' }}
            />
          </div>
        )}
      </div>

      {/* Guide card */}
      <div className="card" style={{ animationDelay: '100ms' }}>
        <div className="card-header">
          <h3>
            <BookOpen size={16} />
            Hướng dẫn sử dụng Superset
          </h3>
        </div>
        <div className="card-body" style={{ lineHeight: 2 }}>
          <p style={{ fontSize: 14, color: '#334155', marginBottom: 12 }}>
            <strong>1.</strong> Nhấn <strong>"Mở Dashboard"</strong> để kết nối — Superset được tự động cấu hình cho tenant của bạn
          </p>
          <p style={{ fontSize: 14, color: '#334155', marginBottom: 12 }}>
            <strong>2.</strong> Dữ liệu được lọc tự động theo tenant qua <strong>Row-Level Security (RLS)</strong> — bạn chỉ thấy dữ liệu của doanh nghiệp mình
          </p>
          <p style={{ fontSize: 14, color: '#334155', marginBottom: 12 }}>
            <strong>3.</strong> Bạn <strong>không thể truy cập Superset trực tiếp</strong> — chỉ xem dashboard được nhúng trong portal
          </p>
          <p style={{ fontSize: 14, color: '#334155' }}>
            <strong>4.</strong> Dashboard được nhúng qua <strong>guest token</strong> với bảo mật RLS đảm bảo cô lập dữ liệu giữa các tenant
          </p>
        </div>
      </div>
    </div>
  );
}
