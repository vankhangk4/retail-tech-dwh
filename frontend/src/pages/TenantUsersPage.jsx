import React, { useState, useEffect } from 'react';
import { getTenantUsers, createTenantUser, deleteTenantUser } from '../services/api';
import {
  Users as UsersIcon,
  Plus,
  Trash2,
  X,
  CheckCircle,
  XCircle,
} from 'lucide-react';

export default function TenantUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ Username: '', Password: '', Email: '' });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await getTenantUsers();
      setUsers(res.data);
    } catch {} finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await createTenantUser(form);
      setShowModal(false);
      setForm({ Username: '', Password: '', Email: '' });
      await loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi khi tạo user');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (userId) => {
    if (!confirm('Xóa user này?')) return;
    try {
      await deleteTenantUser(userId);
      await loadUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Lỗi khi xóa');
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>
            <UsersIcon size={24} style={{ color: '#3b82f6' }} />
            Quản lý Users
          </h1>
          <p>Users trong tenant của bạn</p>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
          <Plus size={16} />
          Tạo User
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>
            <UsersIcon size={16} />
            Danh sách Users ({users.length})
          </h3>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Trạng thái</th>
                  <th>Ngày tạo</th>
                  <th>Hành động</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.UserId}>
                    <td style={{ color: '#94a3b8', fontSize: 13 }}>{u.UserId}</td>
                    <td style={{ fontWeight: 500 }}>{u.Username}</td>
                    <td style={{ color: '#64748b' }}>{u.Email || '-'}</td>
                    <td><span className="badge badge-default">{u.Role}</span></td>
                    <td>
                      <span className={`badge ${u.IsActive ? 'badge-success' : 'badge-danger'}`}>
                        {u.IsActive ? <><CheckCircle size={11} /> Active</> : <><XCircle size={11} /> Inactive</>}
                      </span>
                    </td>
                    <td style={{ color: '#64748b', fontSize: 13 }}>
                      {new Date(u.CreatedAt).toLocaleDateString('vi-VN')}
                    </td>
                    <td>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(u.UserId)}>
                        <Trash2 size={14} />
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Tạo User mới</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={16} />
              </button>
            </div>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Username</label>
                <input type="text" value={form.Username} onChange={(e) => setForm({ ...form, Username: e.target.value })} className="form-input" required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={form.Password} onChange={(e) => setForm({ ...form, Password: e.target.value })} className="form-input" required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.Email} onChange={(e) => setForm({ ...form, Email: e.target.value })} className="form-input" />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowModal(false)}>Hủy</button>
                <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>{saving ? 'Đang lưu...' : 'Lưu'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
