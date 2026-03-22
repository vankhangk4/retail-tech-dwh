import React, { useState, useEffect } from 'react';
import { getTenantUsers, createTenantUser, deleteTenantUser } from '../services/api';

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
      <div className="page-header">
        <h1>Quản lý Users</h1>
        <p>Users trong tenant của bạn</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Danh sách Users ({users.length})</h3>
          <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>
            + Tạo User
          </button>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : (
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
                  <td>{u.UserId}</td>
                  <td>{u.Username}</td>
                  <td>{u.Email || '-'}</td>
                  <td><span className="badge badge-default">{u.Role}</span></td>
                  <td><span className={`badge ${u.IsActive ? 'badge-success' : 'badge-danger'}`}>{u.IsActive ? 'Active' : 'Inactive'}</span></td>
                  <td>{new Date(u.CreatedAt).toLocaleDateString('vi-VN')}</td>
                  <td>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(u.UserId)}>Xóa</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Tạo User mới</h3>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Username</label>
                <input type="text" value={form.Username} onChange={(e) => setForm({ ...form, Username: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={form.Password} onChange={(e) => setForm({ ...form, Password: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.Email} onChange={(e) => setForm({ ...form, Email: e.target.value })} />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-sm" onClick={() => setShowModal(false)}>Hủy</button>
                <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>{saving ? 'Đang lưu...' : 'Lưu'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
