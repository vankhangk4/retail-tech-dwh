import React, { useState, useEffect, useRef } from 'react';
import { uploadFile, listFiles } from '../services/api';
import {
  Upload as UploadIcon,
  FileText,
  FileSpreadsheet,
  X,
  CheckCircle,
  AlertCircle,
  Download,
} from 'lucide-react';

export default function UploadPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragging, setDragging] = useState(false);
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

  const upload = async (file) => {
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

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    await upload(file);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const allowed = ['.csv', '.xlsx', '.xls'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowed.includes(ext)) {
      setError('Chỉ chấp nhận file CSV, XLSX, XLS');
      return;
    }
    await upload(file);
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const fileIcon = (filename) => {
    const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase();
    if (ext === '.csv') return <FileText size={18} style={{ color: '#10b981' }} />;
    if (['.xlsx', '.xls'].includes(ext)) return <FileSpreadsheet size={18} style={{ color: '#059669' }} />;
    return <FileText size={18} style={{ color: '#64748b' }} />;
  };

  return (
    <div>
      <div className="page-header">
        <h1>
          <UploadIcon size={24} style={{ color: '#3b82f6' }} />
          Upload Files
        </h1>
        <p>Tải lên file dữ liệu nguồn (Excel, CSV)</p>
      </div>

      {/* Upload card */}
      <div className="card" style={{ animationDelay: '0ms' }}>
        <div className="card-header">
          <h3>
            <UploadIcon size={16} />
            Tải lên file
          </h3>
        </div>
        <div className="card-body">
          {error && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <AlertCircle size={16} style={{ color: '#dc2626' }} />
              <div className="error-msg" style={{ marginBottom: 0, flex: 1 }}>{error}</div>
            </div>
          )}
          {success && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <CheckCircle size={16} style={{ color: '#059669' }} />
              <div className="success-msg" style={{ marginBottom: 0, flex: 1 }}>{success}</div>
            </div>
          )}
          <div
            className={`upload-area ${dragging ? 'dragging' : ''}`}
            onClick={() => !uploading && fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileChange}
            />
            {uploading ? (
              <div>
                <div className="spinner" style={{ margin: '0 auto 14px', width: 40, height: 40, borderWidth: 3 }}></div>
                <p style={{ fontWeight: 500, color: '#1e293b' }}>Đang upload...</p>
              </div>
            ) : (
              <div>
                <UploadIcon size={40} style={{ marginBottom: 14 }} />
                <p style={{ fontWeight: 600, color: '#1e293b', fontSize: 15 }}>
                  Kéo thả file hoặc click để chọn
                </p>
                <p style={{ fontSize: 13, color: '#94a3b8', marginTop: 6 }}>
                  Hỗ trợ: CSV, XLSX, XLS (tối đa 50MB)
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Files list */}
      <div className="card" style={{ animationDelay: '100ms' }}>
        <div className="card-header">
          <h3>
            <FileText size={16} />
            Files đã upload ({files.length})
          </h3>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div></div>
        ) : files.length === 0 ? (
          <div className="empty-state">
            <FileText size={48} />
            <p style={{ marginTop: 12, fontWeight: 500 }}>Chưa có file nào được upload</p>
            <p style={{ marginTop: 4, fontSize: 13, color: '#94a3b8' }}>
              Upload file CSV hoặc Excel để bắt đầu
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
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
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        {fileIcon(f.filename)}
                        <span style={{ fontWeight: 500 }}>{f.filename}</span>
                      </div>
                    </td>
                    <td style={{ color: '#64748b' }}>{formatSize(f.size)}</td>
                    <td style={{ color: '#64748b', fontSize: 13 }}>
                      {new Date(f.uploaded_at).toLocaleString('vi-VN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
