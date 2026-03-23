import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiLogin, getMe } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Database, Eye, EyeOff, LogIn } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      // Step 1: login to get token
      const res = await apiLogin(username, password);
      const token = res.data.access_token;

      // Step 2: save token so interceptor can attach it
      localStorage.setItem('token', token);

      // Step 3: fetch user data for role
      const meRes = await getMe();
      const userData = meRes.data;

      // Step 4: set auth state, then redirect (replace to avoid back-button issue)
      login(userData);
      const dest = userData.Role === 'SuperAdmin' ? '/admin' : '/dashboard';
      window.location.replace(dest);
    } catch (err) {
      localStorage.removeItem('token');
      setError(err.response?.data?.detail || 'Đăng nhập thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">
            <Database size={28} color="white" />
          </div>
          <h1 className="login-title">DATN Platform</h1>
          <p className="login-subtitle">Đăng nhập để truy cập hệ thống</p>
        </div>

        {error && <div className="error-msg">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Nhập username của bạn"
              className="form-input"
              required
            />
          </div>
          <div className="form-group" style={{ position: 'relative' }}>
            <label>Password</label>
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập password"
              className="form-input"
              style={{ paddingRight: 44 }}
              required
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
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', marginTop: 8, padding: '12px 18px', fontSize: 15 }}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2, marginRight: 4 }}></div>
                Đang đăng nhập...
              </>
            ) : (
              <>
                <LogIn size={18} />
                Đăng nhập
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
