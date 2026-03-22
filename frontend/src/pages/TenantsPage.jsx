import React, { useState, useEffect } from 'react';
import { getTenants, createTenant, deleteTenant } from '../services/api';

export default function TenantsPage() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ TenantId: '', TenantName: '', Plan: 'trial' });
  const [error, setError] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => { loadTenants(); }, []);

  const loadTenants = async () => {
    setLoading(true);
    try {
      const res = await getTenants();
      setTenants(res.data);
    } catch (err) {
      setError('Không thể tải danh sách tenant');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    setError('');
    try {
      await createTenant(form);
      setShowModal(false);
      setForm({ TenantId: '', TenantName: '', Plan: 'trial' });
      await loadTenants();
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi khi tạo tenant');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (tenantId) => {
    if (!confirm(`Xóa tenant "${tenantId}" và toàn bộ dữ liệu?`)) return;
    try {
      await deleteTenant(tenantId);
      await loadTenants();
    } catch (err) {
      alert(err.response?.data?.detail || 'Lỗi khi xóa tenant');
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Quản lý Tenant</h1>
        <p>Tạo và quản lý workspace cho các doanh nghiệp</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Danh sách Tenant ({tenants.length})</h3>
          <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
            + Tạo Tenant mới
          </button>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div>Đang tải...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Tenant ID</th>
                <th>Tên</th>
                <th>Database</th>
                <th>Plan</th>
                <th>Trạng thái</th>
                <th>Ngày tạo</th>
                <th>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((t) => (
                <tr key={t.TenantId}>
                  <td><code>{t.TenantId}</code></td>
                  <td>{t.TenantName}</td>
                  <td><code>{t.DatabaseName}</code></td>
                  <td><span className={`badge badge-${t.Plan === 'trial' ? 'warning' : 'info'}`}>{t.Plan}</span></td>
                  <td><span className={`badge ${t.IsActive ? 'badge-success' : 'badge-danger'}`}>{t.IsActive ? 'Active' : 'Inactive'}</span></td>
                  <td>{new Date(t.CreatedAt).toLocaleDateString('vi-VN')}</td>
                  <td>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(t.TenantId)}>
                      Xóa
                    </button>
                  </td>
                </tr>
              ))}
              {tenants.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', color: '#636e72', padding: '40px' }}>
                    Chưa có tenant nào
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Tạo Tenant mới</h3>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Tenant ID</label>
                <input
                  type="text"
                  value={form.TenantId}
                  onChange={(e) => setForm({ ...form, TenantId: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
                  placeholder="ví dụ: techstore_hcm"
                  required
                />
              </div>
              <div className="form-group">
                <label>Tên Tenant</label>
                <input
                  type="text"
                  value={form.TenantName}
                  onChange={(e) => setForm({ ...form, TenantName: e.target.value })}
                  placeholder="ví dụ: Tech Store HCM"
                  required
                />
              </div>
              <div className="form-group">
                <label>Plan</label>
                <select value={form.Plan} onChange={(e) => setForm({ ...form, Plan: e.target.value })}>
                  <option value="trial">Trial</option>
                  <option value="basic">Basic</option>
                  <option value="pro">Pro</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-sm" onClick={() => setShowModal(false)}>Hủy</button>
                <button type="submit" className="btn btn-primary btn-sm" disabled={creating}>
                  {creating ? 'Đang tạo...' : 'Tạo Tenant'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
