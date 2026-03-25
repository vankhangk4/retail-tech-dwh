import React, { useState, useEffect, useRef } from 'react';
import { uploadFile, listFiles, deleteFile } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  Upload as UploadIcon,
  FileText,
  FileSpreadsheet,
  X,
  CheckCircle,
  AlertCircle,
  Download,
  Eye,
  Trash2,
  RefreshCw,
} from 'lucide-react';

export default function UploadPage() {
  const { impersonatedTenant } = useAuth();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragging, setDragging] = useState(false);
  const [deletingFile, setDeletingFile] = useState(null);
  const [deleteConfirmFile, setDeleteConfirmFile] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Initial state is loading=true, skeleton renders immediately
    loadFiles();
  }, []);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const res = await listFiles();
      setFiles(res.data);
    } catch {} finally {
      setLoading(false);
    }
  };

  const handleDelete = async (filename) => {
    setDeleteConfirmFile(filename);
  };

  const confirmDelete = async () => {
    if (!deleteConfirmFile) return;
    setDeletingFile(deleteConfirmFile);
    setDeleteConfirmFile(null);
    try {
      await deleteFile(deleteConfirmFile);
      await loadFiles();
    } catch (err) {
      alert(err.response?.data?.detail || 'Lỗi khi xóa file');
    } finally {
      setDeletingFile(null);
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
      {impersonatedTenant && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: '#fffbeb', border: '1px solid #fcd34d',
          borderRadius: 10, padding: '10px 14px', marginBottom: 20,
        }}>
          <Eye size={16} style={{ color: '#d97706' }} />
          <span style={{ fontSize: 13, color: '#92400e', fontWeight: 500 }}>
            Đang xem dữ liệu của tenant <strong>{impersonatedTenant}</strong>
          </span>
          <span style={{ fontSize: 12, color: '#b45309' }}>
            (SuperAdmin impersonation)
          </span>
        </div>
      )}

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
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Tên file</th>
                  <th>Kích thước</th>
                  <th>Ngày upload</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3].map((i) => (
                  <tr key={i}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div className="skeleton" style={{ width: 18, height: 18, borderRadius: 4 }} />
                        <div className="skeleton" style={{ width: 160, height: 14 }} />
                      </div>
                    </td>
                    <td><div className="skeleton" style={{ width: 60, height: 14 }} /></td>
                    <td><div className="skeleton" style={{ width: 140, height: 14 }} /></td>
                    <td></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
                  <th></th>
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
                    <td>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleDelete(f.filename)}
                        disabled={deletingFile === f.filename}
                        title="Xóa file"
                        style={{ color: '#dc2626', borderColor: '#fca5a5' }}
                        onMouseEnter={(e) => { e.currentTarget.style.background = '#fef2f2'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = ''; }}
                      >
                        {deletingFile === f.filename ? (
                          <RefreshCw size={14} className="animate-spin" />
                        ) : (
                          <Trash2 size={14} />
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirmFile && (
        <div className="modal-overlay" onClick={() => setDeleteConfirmFile(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 420 }}>
            <div className="modal-header">
              <h3>Xác nhận xóa file</h3>
              <button className="modal-close" onClick={() => setDeleteConfirmFile(null)}>
                <X size={16} />
              </button>
            </div>
            <div style={{ padding: '20px 24px' }}>
              <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <div style={{
                  width: 56, height: 56, borderRadius: '50%',
                  background: '#fef2f2', margin: '0 auto 16px',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Trash2 size={24} style={{ color: '#dc2626' }} />
                </div>
                <p style={{ fontSize: 15, color: '#1e293b', marginBottom: 8 }}>
                  Bạn có chắc chắn muốn xóa file?
                </p>
                <p style={{ fontSize: 13, color: '#64748b', fontFamily: 'monospace' }}>
                  {deleteConfirmFile}
                </p>
                <div style={{
                  marginTop: 12, padding: '10px 14px',
                  background: '#fef2f2', border: '1px solid #fca5a5',
                  borderRadius: 8, textAlign: 'left',
                }}>
                  <p style={{ fontSize: 13, color: '#dc2626', fontWeight: 600, marginBottom: 4 }}>
                    Cảnh báo: Thao tác này sẽ xóa:
                  </p>
                  <ul style={{ fontSize: 12, color: '#991b1b', margin: 0, paddingLeft: 18 }}>
                    <li>File đã upload</li>
                    <li>Toàn bộ dữ liệu đã ETL (staging, dimension, fact tables)</li>
                    <li>Lịch sử ETL run của tenant này</li>
                  </ul>
                  <p style={{ fontSize: 12, color: '#dc2626', marginTop: 6, marginBottom: 0 }}>
                    Thao tác này không thể hoàn tác.
                  </p>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
                <button
                  className="btn btn-secondary"
                  onClick={() => setDeleteConfirmFile(null)}
                  disabled={deletingFile}
                >
                  Hủy
                </button>
                <button
                  className="btn btn-danger"
                  onClick={confirmDelete}
                  disabled={deletingFile}
                  style={{ display: 'flex', alignItems: 'center', gap: 6 }}
                >
                  {deletingFile ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" />
                      Đang xóa...
                    </>
                  ) : (
                    <>
                      <Trash2 size={14} />
                      Xóa file
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
