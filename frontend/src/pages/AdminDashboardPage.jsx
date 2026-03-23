import React, { useState, useEffect } from 'react';
import { getETLHistory, getAdminStats } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  Building2,
  Users,
  RefreshCw,
  TrendingUp,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
} from 'lucide-react';

export default function AdminDashboardPage() {
  const { impersonatedTenant } = useAuth();
  const [stats, setStats] = useState({ tenants: 0, users: 0, etlRuns: 0 });
  const [recentETL, setRecentETL] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, etlRes] = await Promise.all([
        getAdminStats(),
        getETLHistory(),
      ]);
      setStats({
        tenants: statsRes.data.tenants ?? 0,
        users: statsRes.data.users ?? 0,
        etlRuns: statsRes.data.etl_runs ?? 0,
      });
      setRecentETL(etlRes.data.slice(0, 5));
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const statusColor = (s) => {
    if (s === 'SUCCESS') return '#10b981';
    if (s === 'FAILED') return '#ef4444';
    if (s === 'RUNNING') return '#3b82f6';
    return '#94a3b8';
  };

  const statusIcon = (s) => {
    if (s === 'SUCCESS') return <CheckCircle size={13} />;
    if (s === 'FAILED') return <XCircle size={13} />;
    if (s === 'RUNNING') return <RefreshCw size={13} className="spin" />;
    return <Clock size={13} />;
  };

  return (
    <div>
      {/* Impersonation banner */}
      {impersonatedTenant && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: '#fffbeb', border: '1px solid #fcd34d',
          borderRadius: 10, padding: '10px 14px', marginBottom: 20,
        }}>
          <Eye size={16} style={{ color: '#d97706' }} />
          <span style={{ fontSize: 13, color: '#92400e', fontWeight: 500 }}>
            Đang xem dashboard của tenant <strong>{impersonatedTenant}</strong>
          </span>
          <span style={{ fontSize: 12, color: '#b45309' }}>(SuperAdmin impersonation)</span>
        </div>
      )}

      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>
            <TrendingUp size={24} style={{ color: '#3b82f6' }} />
            Tổng quan
          </h1>
          <p>Thống kê hệ thống Data Warehouse</p>
        </div>
      </div>

      {/* Stats cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 16,
        marginBottom: 24,
      }}>
        {[
          { label: 'Tổng Tenant', value: stats.tenants, icon: Building2, color: '#3b82f6', bg: '#eff6ff' },
          { label: 'Tổng Users', value: stats.users, icon: Users, color: '#8b5cf6', bg: '#f5f3ff' },
          { label: 'ETL Runs', value: stats.etlRuns, icon: RefreshCw, color: '#f59e0b', bg: '#fffbeb' },
        ].map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="card" style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '20px 24px' }}>
              {loading ? (
                <>
                  <div className="skeleton" style={{ width: 44, height: 44, borderRadius: 12, flexShrink: 0 }} />
                  <div>
                    <div className="skeleton" style={{ width: 48, height: 28, marginBottom: 6 }} />
                    <div className="skeleton" style={{ width: 80, height: 12 }} />
                  </div>
                </>
              ) : (
                <>
                  <div style={{
                    width: 44, height: 44, borderRadius: 12,
                    background: card.bg, display: 'flex',
                    alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  }}>
                    <Icon size={22} style={{ color: card.color }} />
                  </div>
                  <div>
                    <div style={{ fontSize: 26, fontWeight: 700, color: '#1e293b', lineHeight: 1 }}>
                      {card.value}
                    </div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{card.label}</div>
                  </div>
                </>
              )}
            </div>
          );
        })}
      </div>

      {/* Recent ETL runs */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <RefreshCw size={18} style={{ color: '#3b82f6' }} />
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>ETL gần đây</h3>
        </div>
        {loading ? (
          <table className="table">
            <thead>
              <tr>
                <th>Tenant</th>
                <th>Trạng thái</th>
                <th>Bắt đầu</th>
                <th>Hoàn thành</th>
                <th>Lỗi</th>
              </tr>
            </thead>
            <tbody>
              {[1, 2, 3, 4, 5].map((i) => (
                <tr key={i}>
                  <td><div className="skeleton" style={{ width: 60, height: 18, borderRadius: 4 }} /></td>
                  <td><div className="skeleton" style={{ width: 80, height: 18, borderRadius: 999 }} /></td>
                  <td><div className="skeleton" style={{ width: 140, height: 14 }} /></td>
                  <td><div className="skeleton" style={{ width: 140, height: 14 }} /></td>
                  <td><div className="skeleton" style={{ width: 100, height: 14 }} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : recentETL.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 20, color: '#94a3b8' }}>Chưa có ETL run nào</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Tenant</th>
                <th>Trạng thái</th>
                <th>Bắt đầu</th>
                <th>Hoàn thành</th>
                <th>Lỗi</th>
              </tr>
            </thead>
            <tbody>
              {recentETL.map((r) => (
                <tr key={r.run_id}>
                  <td><span className="badge badge-blue">{r.tenant_id}</span></td>
                  <td>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 4,
                      color: statusColor(r.status), fontWeight: 500, fontSize: 13,
                    }}>
                      {statusIcon(r.status)}
                      {r.status}
                    </span>
                  </td>
                  <td style={{ color: '#64748b', fontSize: 13 }}>
                    {r.started_at ? new Date(r.started_at).toLocaleString('vi-VN') : '—'}
                  </td>
                  <td style={{ color: '#64748b', fontSize: 13 }}>
                    {r.completed_at ? new Date(r.completed_at).toLocaleString('vi-VN') : '—'}
                  </td>
                  <td style={{ color: '#ef4444', fontSize: 12, maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {r.error || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
