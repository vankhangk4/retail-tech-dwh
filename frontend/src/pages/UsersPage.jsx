import React, { useState, useEffect } from 'react';
import { getUsers, createUser, updateUser, deleteUser } from '../services/api';
import {
  Users as UsersIcon,
  Plus,
  Pencil,
  Trash2,
  X,
  Shield,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
} from 'lucide-react';

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [form, setForm] = useState({ Username: '', Password: '', Email: '', Role: 'User', TenantId: '' });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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
    setShowPassword(false);
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

  const roleBadge = (role) => {
    const map = { SuperAdmin: 'danger', TenantAdmin: 'info', User: 'default' };
    return <span className={`badge badge-${map[role] || 'default'}`}><Shield size={11} />{role}</span>;
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>
            <UsersIcon size={24} style={{ color: '#3b82f6' }} />
            Quản lý Users
          </h1>
          <p>Tất cả users trên hệ thống</p>
        </div>
        <button
          className="btn btn-primary btn-sm"
          onClick={() => {
            setEditUser(null);
            setForm({ Username: '', Password: '', Email: '', Role: 'User', TenantId: '' });
            setShowPassword(false);
            setShowModal(true);
          }}
        >
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
                    <td style={{ color: '#94a3b8', fontSize: 13 }}>{u.UserId}</td>
                    <td style={{ fontWeight: 500 }}>{u.Username}</td>
                    <td style={{ color: '#64748b' }}>{u.Email || '-'}</td>
                    <td>
                      {u.TenantId ? (
                        <code style={{ background: '#eff6ff', color: '#1d4ed8', padding: '2px 8px', borderRadius: 6, fontSize: 12 }}>{u.TenantId}</code>
                      ) : (
                        <span style={{ color: '#059669', fontWeight: 600, fontSize: 12 }}>SuperAdmin</span>
                      )}
                    </td>
                    <td>{roleBadge(u.Role)}</td>
                    <td>
                      <span className={`badge ${u.IsActive ? 'badge-success' : 'badge-danger'}`}>
                        {u.IsActive ? <><CheckCircle size={11} /> Active</> : <><XCircle size={11} /> Inactive</>}
                      </span>
                    </td>
                    <td style={{ color: '#64748b', fontSize: 13 }}>
                      {new Date(u.CreatedAt).toLocaleDateString('vi-VN')}
                    </td>
                    <td>
                      <div className="table-actions">
                        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => handleEdit(u)} title="Sửa">
                          <Pencil size={14} style={{ color: '#3b82f6' }} />
                        </button>
                        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => handleDelete(u.UserId)} title="Xóa">
                          <Trash2 size={14} style={{ color: '#dc2626' }} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => { setShowModal(false); setShowPassword(false); }}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editUser ? 'Sửa User' : 'Tạo User mới'}</h3>
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
              <div className="form-group" style={{ position: 'relative' }}>
                <label>Password {editUser && '(bỏ trống nếu không đổi)'}</label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={form.Password}
                  onChange={(e) => setForm({ ...form, Password: e.target.value })}
                  className="form-input"
                  placeholder={editUser ? '••••••' : ''}
                  required={!editUser}
                  style={{ paddingRight: 44 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: 12,
                    top: 34,
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#94a3b8',
                    padding: 0,
                    display: 'flex',
                  }}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={form.Email} onChange={(e) => setForm({ ...form, Email: e.target.value })} className="form-input" />
              </div>
              <div className="form-group">
                <label>Role</label>
                <select value={form.Role} onChange={(e) => setForm({ ...form, Role: e.target.value })} className="form-select">
                  <option value="User">User</option>
                  <option value="TenantAdmin">TenantAdmin</option>
                  <option value="SuperAdmin">SuperAdmin</option>
                </select>
              </div>
              <div className="form-group">
                <label>Tenant ID {form.Role === 'SuperAdmin' && '(bỏ trống)'}</label>
                <input
                  type="text"
                  value={form.TenantId}
                  onChange={(e) => setForm({ ...form, TenantId: e.target.value })}
                  className="form-input"
                  placeholder={form.Role === 'SuperAdmin' ? 'SuperAdmin' : 'ví dụ: techstore_hcm'}
                  disabled={form.Role === 'SuperAdmin'}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowModal(false)}>Hủy</button>
                <button type="submit" className="btn btn-primary btn-sm" disabled={saving}>
                  {saving ? 'Đang lưu...' : 'Lưu'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
