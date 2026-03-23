import React, { useState, useEffect } from 'react';
import { getTenants, createTenant, deleteTenant } from '../services/api';
import {
  Building2,
  Plus,
  Trash2,
  X,
  Search,
  Server,
  CheckCircle,
  XCircle,
} from 'lucide-react';

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

  const planBadge = (plan) => {
    const colors = { trial: 'warning', basic: 'info', pro: 'success' };
    return <span className={`badge badge-${colors[plan] || 'default'}`}>{plan}</span>;
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>
            <Building2 size={24} style={{ color: '#3b82f6' }} />
            Quản lý Tenant
          </h1>
          <p>Tạo và quản lý workspace cho các doanh nghiệp</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
          <Plus size={16} />
          Tạo Tenant
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>
            <Server size={16} />
            Danh sách Tenant ({tenants.length})
          </h3>
        </div>

        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        ) : (
          <div className="table-wrapper">
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
                    <td>
                      <code style={{
                        background: '#eff6ff',
                        color: '#1d4ed8',
                        padding: '2px 8px',
                        borderRadius: 6,
                        fontSize: 13,
                        fontWeight: 600,
                      }}>{t.TenantId}</code>
                    </td>
                    <td style={{ fontWeight: 500 }}>{t.TenantName}</td>
                    <td>
                      <code style={{
                        background: '#f8fafc',
                        color: '#64748b',
                        padding: '2px 8px',
                        borderRadius: 6,
                        fontSize: 12,
                      }}>{t.DatabaseName}</code>
                    </td>
                    <td>{planBadge(t.Plan)}</td>
                    <td>
                      <span className={`badge ${t.IsActive ? 'badge-success' : 'badge-danger'}`}>
                        {t.IsActive ? (
                          <><CheckCircle size={12} /> Active</>
                        ) : (
                          <><XCircle size={12} /> Inactive</>
                        )}
                      </span>
                    </td>
                    <td style={{ color: '#64748b', fontSize: 13 }}>
                      {new Date(t.CreatedAt).toLocaleDateString('vi-VN')}
                    </td>
                    <td>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(t.TenantId)}
                      >
                        <Trash2 size={14} />
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))}
                {tenants.length === 0 && (
                  <tr>
                    <td colSpan={7}>
                      <div className="empty-state">
                        <Building2 size={40} />
                        <p>Chưa có tenant nào</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Tạo Tenant mới</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={16} />
              </button>
            </div>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Tenant ID</label>
                <input
                  type="text"
                  value={form.TenantId}
                  onChange={(e) => setForm({ ...form, TenantId: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
                  placeholder="ví dụ: techstore_hcm"
                  className="form-input"
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
                  className="form-input"
                  required
                />
              </div>
              <div className="form-group">
                <label>Plan</label>
                <select
                  value={form.Plan}
                  onChange={(e) => setForm({ ...form, Plan: e.target.value })}
                  className="form-select"
                >
                  <option value="trial">Trial</option>
                  <option value="basic">Basic</option>
                  <option value="pro">Pro</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowModal(false)}>
                  Hủy
                </button>
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
