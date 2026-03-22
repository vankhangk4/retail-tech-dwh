import React, { useState, useEffect } from 'react';
import { getUsers, createUser, updateUser, deleteUser } from '../services/api';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [form, setForm] = useState({ Username: '', Password: '', Email: '', Role: 'User', TenantId: '' });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await getUsers();
      setUsers(res.data);
    } catch (err) {
      setError('Không thể tải users');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = { ...form };
      if (!payload.Password) delete payload.Password;
      if (editUser) {
        await updateUser(editUser.UserId, payload);
      } else {
        await createUser(payload);
      }
      setShowModal(false);
      setEditUser(null);
      setForm({ Username: '', Password: '', Email: '', Role: 'User', TenantId: '' });
      await loadUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi khi lưu');
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (user) => {
    setEditUser(user);
    setForm({ Username: user.Username, Password: '', Email: user.Email || '', Role: user.Role, TenantId: user.TenantId || '' });
    setShowModal(true);
  };

  const handleDelete = async (userId) => {
    if (!confirm('Xóa user này?')) return;
    try {
      await deleteUser(userId);
      await loadUsers();
    } catch (err) {
      alert(err.response?.data?.detail || 'Lỗi khi xóa');
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Quản lý Users</h1>
        <p>Tất cả users trên hệ thống</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Danh sách Users ({users.length})</h3>
          <button className="btn btn-primary btn-sm" onClick={() => { setEditUser(null); setForm({ Username: '', Password: '', Email: '', Role: 'User', TenantId: '' }); setShowModal(true); }}>
            + Tạo User mới
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
                <th>Tenant</th>
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
                  <td>{u.TenantId || <span style={{ color: '#27ae60', fontWeight: 500 }}>SuperAdmin</span>}</td>
                  <td><span className={`badge badge-${u.Role === 'SuperAdmin' ? 'danger' : u.Role === 'TenantAdmin' ? 'info' : 'default'}`}>{u.Role}</span></td>
                  <td><span className={`badge ${u.IsActive ? 'badge-success' : 'badge-danger'}`}>{u.IsActive ? 'Active' : 'Inactive'}</span></td>
                  <td>{new Date(u.CreatedAt).toLocaleDateString('vi-VN')}</td>
                  <td>
                    <button className="btn btn-sm" style={{ marginRight: 6 }} onClick={() => handleEdit(u)}>Sửa</button>
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
            <h3>{editUser ? 'Sửa User' : 'Tạo User mới'}</h3>
            {error && <div className="error-msg">{error}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Username</label>
                <input type="text" value={form.Username} onChange={(e) => setForm({ ...form, Username: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Password {editUser && '(bỏ trống nếu không đổi)'}</label>
                <input type="password" value={form.Password} onChange={(e) => setForm({ ...form, Password: e.target.value })} placeholder={editUser ? '••••••' : ''} required={!editUser} />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.Email} onChange={(e) => setForm({ ...form, Email: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Role</label>
                <select value={form.Role} onChange={(e) => setForm({ ...form, Role: e.target.value })}>
                  <option value="User">User</option>
                  <option value="TenantAdmin">TenantAdmin</option>
                  <option value="SuperAdmin">SuperAdmin</option>
                </select>
              </div>
              <div className="form-group">
                <label>Tenant ID {form.Role === 'SuperAdmin' && '(bỏ trống)'}</label>
                <input type="text" value={form.TenantId} onChange={(e) => setForm({ ...form, TenantId: e.target.value })} placeholder={form.Role === 'SuperAdmin' ? 'SuperAdmin' : 'ví dụ: techstore_hcm'} disabled={form.Role === 'SuperAdmin'} />
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
