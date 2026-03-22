import React, { useState, useEffect, useRef } from 'react';
import { uploadFile, listFiles } from '../services/api';

export default function UploadPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => { loadFiles(); }, []);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const res = await listFiles();
      setFiles(res.data);
    } catch {} finally {
      setLoading(false);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError('');
    setSuccess('');
    try {
      await uploadFile(file);
      setSuccess(`Đã upload "${file.name}" thành công`);
      await loadFiles();
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi khi upload file');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>Upload Files</h1>
        <p>Tải lên file dữ liệu nguồn (Excel, CSV)</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Tải lên file</h3>
        </div>
        {error && <div className="error-msg">{error}</div>}
        {success && <div style={{ color: '#27ae60', padding: 8, background: '#e8f8f0', borderRadius: 6, marginBottom: 15, fontSize: 13 }}>{success}</div>}
        <div
          className="upload-area"
          onClick={() => !uploading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
          />
          {uploading ? (
            <div>
              <div className="spinner" style={{ margin: '0 auto 12px' }}></div>
              <p>Đang upload...</p>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: 40, marginBottom: 12 }}>📁</p>
              <p style={{ fontWeight: 500 }}>Click để chọn file</p>
              <p style={{ fontSize: 13, color: '#636e72', marginTop: 4 }}>Hỗ trợ: CSV, XLSX, XLS</p>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Files đã upload ({files.length})</h3>
        </div>
        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : files.length === 0 ? (
          <div className="empty-state">
            <p>Chưa có file nào được upload</p>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Tên file</th>
                <th>Kích thước</th>
                <th>Ngày upload</th>
              </tr>
            </thead>
            <tbody>
              {files.map((f) => (
                <tr key={f.filename}>
                  <td>{f.filename}</td>
                  <td>{(f.size / 1024).toFixed(1)} KB</td>
                  <td>{new Date(f.uploaded_at).toLocaleString('vi-VN')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
