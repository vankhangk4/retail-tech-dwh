import React, { useState } from 'react';
import { getSupersetToken } from '../services/api';

export default function ReportsPage() {
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const supersetUrl = 'http://localhost:8088';

  const openSuperset = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await getSupersetToken();
      setToken(res.data.token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể lấy Superset token');
    } finally {
      setLoading(false);
    }
  };

  const dashboardUrl = token
    ? `${supersetUrl}/superset/dashboard/1/?preserve_hash=true&guest_token=${token}`
    : null;

  return (
    <div>
      <div className="page-header">
        <h1>Reports & Dashboards</h1>
        <p>Xem báo cáo trực quan hóa dữ liệu trên Superset</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Apache Superset</h3>
          {!token && (
            <button className="btn btn-primary btn-sm" onClick={openSuperset} disabled={loading}>
              {loading ? 'Đang kết nối...' : 'Mở Superset Dashboard'}
            </button>
          )}
        </div>

        {error && <div className="error-msg">{error}</div>}

        {!token ? (
          <div className="empty-state">
            <p style={{ fontSize: 48, marginBottom: 16 }}>📊</p>
            <p>Nhấn "Mở Superset Dashboard" để truy cập báo cáo.</p>
            <p style={{ fontSize: 13, color: '#636e72', marginTop: 8 }}>
              Đảm bảo Superset đang chạy tại {supersetUrl}
            </p>
          </div>
        ) : (
          <div className="superset-container">
            <div className="superset-header">
              <h3>📊 Superset Dashboard</h3>
            </div>
            <iframe
              src={`${supersetUrl}/superset/dashboard/1/?guest_token=${token}`}
              className="superset-iframe"
              title="Superset Dashboard"
              allow="fullscreen"
            />
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Hướng dẫn sử dụng Superset</h3>
        </div>
        <div style={{ fontSize: 14, color: '#636e72', lineHeight: 1.8 }}>
          <p>1. Đảm bảo Superset đang chạy tại <code>{supersetUrl}</code></p>
          <p>2. Đăng nhập Superset với username/password: <code>admin</code> / <code>Dk@17092004</code></p>
          <p>3. Kết nối database: <code>DWH_{'{tenant_id}'}</code> (Superset Admin tạo kết nối)</p>
          <p>4. Tạo dataset từ các bảng Fact/Dim</p>
          <p>5. Tạo chart và dashboard</p>
          <p>6. Dashboard được nhúng vào portal qua guest token</p>
        </div>
      </div>
    </div>
  );
}
