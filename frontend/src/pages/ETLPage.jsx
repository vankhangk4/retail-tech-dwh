import React, { useState, useEffect } from 'react';
import { getETLHistory, triggerETL, getETLStatus } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function ETLPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [latestRunId, setLatestRunId] = useState(null);
  const [polling, setPolling] = useState(false);

  useEffect(() => { loadHistory(); }, []);

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
    try {
      const res = await getETLHistory();
      setHistory(res.data);
    } catch {
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

  const statusBadge = (status) => {
    const map = {
      PENDING: 'warning', RUNNING: 'info', SUCCESS: 'success', FAILED: 'danger',
    };
    const labels = {
      PENDING: 'Chờ', RUNNING: 'Đang chạy', SUCCESS: 'Thành công', FAILED: 'Thất bại',
    };
    return <span className={`badge badge-${map[status] || 'default'}`}>{labels[status] || status}</span>;
  };

  return (
    <div>
      <div className="page-header">
        <h1>ETL Pipeline</h1>
        <p>Quản lý và theo dõi quá trình ETL</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Lịch sử ETL Runs</h3>
          <button className="btn btn-primary btn-sm" onClick={handleTrigger} disabled={triggering}>
            {triggering ? 'Đang kích hoạt...' : '+ Chạy ETL'}
          </button>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : (
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
              {history.map((r) => (
                <tr key={r.run_id}>
                  <td>{r.run_id}</td>
                  {user.Role === 'SuperAdmin' && <td><code>{r.tenant_id}</code></td>}
                  <td>{statusBadge(r.status)}</td>
                  <td>{r.rows_processed?.toLocaleString() || 0}</td>
                  <td>{r.started_at ? new Date(r.started_at).toLocaleString('vi-VN') : '-'}</td>
                  <td>{r.completed_at ? new Date(r.completed_at).toLocaleString('vi-VN') : '-'}</td>
                  <td style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.error || '-'}</td>
                </tr>
              ))}
              {history.length === 0 && (
                <tr><td colSpan={user.Role === 'SuperAdmin' ? 7 : 6} style={{ textAlign: 'center', padding: 40 }}>Chưa có ETL run nào</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
