import React, { useState, useEffect } from 'react';
import { getETLHistory, triggerETL, getETLStatus } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  RefreshCw,
  Play,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Activity,
} from 'lucide-react';

export default function ETLPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [latestRunId, setLatestRunId] = useState(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Initial state is loading=true, skeleton renders immediately
    loadHistory();
  }, []);

  useEffect(() => {
    if (!latestRunId) return;
    const poll = setInterval(async () => {
      try {
        const res = await getETLStatus(latestRunId);
        if (['SUCCESS', 'FAILED'].includes(res.data.status)) {
          setPolling(false);
          clearInterval(poll);
          await loadHistory();
        }
      } catch {}
    }, 3000);
    return () => clearInterval(poll);
  }, [latestRunId]);

  const loadHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await getETLHistory();
      setHistory(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể tải lịch sử ETL');
    } finally {
      setLoading(false);
    }
  };

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      const res = await triggerETL();
      setLatestRunId(res.data.run_id);
      setPolling(true);
      await loadHistory();
    } catch (err) {
      alert(err.response?.data?.detail || 'Lỗi khi kích hoạt ETL');
    } finally {
      setTriggering(false);
    }
  };

  const statusConfig = (status) => {
    const map = {
      PENDING: { icon: Clock, cls: 'badge-warning', label: 'Chờ', color: '#d97706' },
      RUNNING: { icon: Activity, cls: 'badge-info', label: 'Đang chạy', color: '#2563eb' },
      SUCCESS: { icon: CheckCircle, cls: 'badge-success', label: 'Thành công', color: '#059669' },
      FAILED: { icon: XCircle, cls: 'badge-danger', label: 'Thất bại', color: '#dc2626' },
    };
    return map[status] || { icon: AlertCircle, cls: 'badge-default', label: status, color: '#64748b' };
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>
            <RefreshCw size={24} style={{ color: '#3b82f6' }} />
            ETL Pipeline
          </h1>
          <p>Quản lý và theo dõi quá trình ETL</p>
        </div>
        <button
          className="btn btn-primary btn-sm"
          onClick={handleTrigger}
          disabled={triggering}
        >
          {triggering || polling ? (
            <>
              <div className="spinner" style={{ width: 14, height: 14, borderWidth: 2, marginRight: 4 }}></div>
              Đang chạy...
            </>
          ) : (
            <>
              <Play size={16} />
              Chạy ETL
            </>
          )}
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="card" style={{ marginBottom: 20, borderLeft: '4px solid #dc2626' }}>
          <div className="card-body" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <AlertCircle size={20} style={{ color: '#dc2626' }} />
            <p style={{ fontWeight: 600, color: '#dc2626' }}>{error}</p>
          </div>
        </div>
      )}

      {/* Status bar when polling */}
      {polling && (
        <div className="card" style={{ animationDelay: '0ms', borderLeft: '4px solid #3b82f6' }}>
          <div className="card-body" style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 20px' }}>
            <Activity size={18} style={{ color: '#3b82f6' }} className="animate-pulse" />
            <span style={{ fontSize: 14, color: '#3b82f6', fontWeight: 500 }}>ETL đang được xử lý...</span>
            <span style={{ fontSize: 12, color: '#94a3b8', marginLeft: 'auto' }}>
              Tự động cập nhật mỗi 3 giây
            </span>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3>
            <Activity size={16} />
            Lịch sử ETL Runs
          </h3>
          <button
            className="btn btn-secondary btn-sm"
            onClick={loadHistory}
            disabled={loading}
          >
            <RefreshCw size={14} />
            Làm mới
          </button>
        </div>

        {loading ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Run ID</th>
                  {user.Role === 'SuperAdmin' && <th>Tenant</th>}
                  <th>Trạng thái</th>
                  <th>Bản ghi</th>
                  <th>Bắt đầu</th>
                  <th>Hoàn thành</th>
                  <th>Lỗi</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3].map((i) => (
                  <tr key={i}>
                    <td><div className="skeleton" style={{ width: 120, height: 16 }} /></td>
                    {user.Role === 'SuperAdmin' && <td><div className="skeleton" style={{ width: 80, height: 22, borderRadius: 6 }} /></td>}
                    <td><div className="skeleton" style={{ width: 90, height: 22, borderRadius: 999 }} /></td>
                    <td><div className="skeleton" style={{ width: 60, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 130, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 130, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 80, height: 16 }} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Run ID</th>
                  {user.Role === 'SuperAdmin' && <th>Tenant</th>}
                  <th>Trạng thái</th>
                  <th>Bản ghi</th>
                  <th>Bắt đầu</th>
                  <th>Hoàn thành</th>
                  <th>Lỗi</th>
                </tr>
              </thead>
              <tbody>
                {history.map((r) => {
                  const cfg = statusConfig(r.status);
                  const StatusIcon = cfg.icon;
                  return (
                    <tr key={r.run_id}>
                      <td style={{ color: '#64748b', fontSize: 13, fontFamily: 'monospace' }}>{r.run_id}</td>
                      {user.Role === 'SuperAdmin' && (
                        <td>
                          <code style={{ background: '#eff6ff', color: '#1d4ed8', padding: '2px 8px', borderRadius: 6, fontSize: 12 }}>
                            {r.tenant_id}
                          </code>
                        </td>
                      )}
                      <td>
                        <span className={`badge ${cfg.cls}`}>
                          <StatusIcon size={12} />
                          {cfg.label}
                        </span>
                      </td>
                      <td style={{ fontWeight: 600, color: '#0f172a' }}>
                        {r.rows_processed?.toLocaleString() || 0}
                      </td>
                      <td style={{ color: '#64748b', fontSize: 13 }}>
                        {r.started_at ? new Date(r.started_at).toLocaleString('vi-VN') : '-'}
                      </td>
                      <td style={{ color: '#64748b', fontSize: 13 }}>
                        {r.completed_at ? new Date(r.completed_at).toLocaleString('vi-VN') : '-'}
                      </td>
                      <td>
                        {r.error ? (
                          <span style={{ color: '#dc2626', fontSize: 13, maxWidth: 200, display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {r.error}
                          </span>
                        ) : (
                          <span style={{ color: '#cbd5e1' }}>-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {history.length === 0 && (
                  <tr>
                    <td colSpan={user.Role === 'SuperAdmin' ? 7 : 6}>
                      <div className="empty-state">
                        <RefreshCw size={40} />
                        <p>Chưa có ETL run nào</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
