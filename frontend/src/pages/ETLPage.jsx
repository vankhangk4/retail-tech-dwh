import React, { useState, useEffect } from 'react';
import { getETLHistory, triggerETL, getETLStatus, getETLLogs } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  RefreshCw,
  Play,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Activity,
  Eye,
  FileText,
  X,
} from 'lucide-react';

export default function ETLPage() {
  const { user, impersonatedTenant } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [latestRunId, setLatestRunId] = useState(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState('');
  const [showLogModal, setShowLogModal] = useState(false);
  const [logRunId, setLogRunId] = useState(null);
  const [logContent, setLogContent] = useState('');
  const [logLoading, setLogLoading] = useState(false);

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

          if (res.data.status === 'SUCCESS') {
            localStorage.setItem('last_etl_success_at', String(Date.now()));
            window.dispatchEvent(new Event('etl-success'));
          }

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

  const openLogModal = async (runId) => {
    setShowLogModal(true);
    setLogRunId(runId);
    setLogLoading(true);
    try {
      const res = await getETLLogs(runId);
      setLogContent(res.data.log_output || '(Không có log)');
    } catch {
      setLogContent('Không thể tải log');
    } finally {
      setLogLoading(false);
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
      {impersonatedTenant && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: '#fffbeb', border: '1px solid #fcd34d',
          borderRadius: 10, padding: '10px 14px', marginBottom: 20,
        }}>
          <Eye size={16} style={{ color: '#d97706' }} />
          <span style={{ fontSize: 13, color: '#92400e', fontWeight: 500 }}>
            Đang xem dữ liệu của tenant <strong>{impersonatedTenant}</strong>
          </span>
          <span style={{ fontSize: 12, color: '#b45309' }}>
            (SuperAdmin impersonation)
          </span>
        </div>
      )}

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
                  <th>Log</th>
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
                  <th>Log</th>
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
                      <td>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => openLogModal(r.run_id)}
                          style={{ fontSize: 12, padding: '2px 8px' }}
                          title="Xem log"
                        >
                          <FileText size={12} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {history.length === 0 && (
                  <tr>
                    <td colSpan={user.Role === 'SuperAdmin' ? 8 : 7}>
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

      {/* Log Modal */}
      {showLogModal && (
        <div className="modal-overlay" onClick={() => setShowLogModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 800 }}>
            <div className="modal-header">
              <h3>ETL Log — Run #{logRunId}</h3>
              <button className="modal-close" onClick={() => setShowLogModal(false)}>
                <X size={16} />
              </button>
            </div>
            <div style={{ padding: '16px 20px', maxHeight: 500, overflow: 'auto' }}>
              {logLoading ? (
                <div style={{ textAlign: 'center', padding: 20 }}>
                  <div className="spinner" style={{ margin: '0 auto' }}></div>
                  <p style={{ marginTop: 12, color: '#94a3b8' }}>Đang tải log...</p>
                </div>
              ) : (
                <pre style={{
                  fontFamily: 'monospace', fontSize: 12,
                  background: '#0f172a', color: '#e2e8f0',
                  padding: 16, borderRadius: 8,
                  overflow: 'auto', maxHeight: 450,
                  whiteSpace: 'pre-wrap', wordBreak: 'break-all',
                  lineHeight: 1.6, margin: 0,
                }}>
                  {logContent || '(Không có log)'}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
