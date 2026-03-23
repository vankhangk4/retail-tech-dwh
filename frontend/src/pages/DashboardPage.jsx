import React, { useState, useEffect } from 'react';
import { getStats, getSummary } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  TrendingUp,
  ShoppingCart,
  Users,
  Package,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  AlertCircle,
  Eye,
} from 'lucide-react';

export default function DashboardPage() {
  const { impersonatedTenant } = useAuth();
  const [stats, setStats] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Initial state is loading=true, skeleton renders immediately
    // Data loads in background, UI stays responsive
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [s1, s2] = await Promise.all([getStats(), getSummary()]);
      setStats(s1.data);
      setSummary(s2.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      label: 'Tổng doanh thu',
      value: stats?.total_revenue?.toLocaleString('vi-VN') + 'đ' || '0đ',
      icon: TrendingUp,
      iconColor: 'blue',
      sub: 'Từ FactSales',
    },
    {
      label: 'Tổng đơn hàng',
      value: stats?.total_orders?.toLocaleString() || '0',
      icon: ShoppingCart,
      iconColor: 'green',
      sub: 'Hóa đơn bán hàng',
    },
    {
      label: 'Tổng khách hàng',
      value: stats?.total_customers?.toLocaleString() || '0',
      icon: Users,
      iconColor: 'purple',
      sub: 'Trong DimCustomer',
    },
    {
      label: 'Sản phẩm theo dõi',
      value: stats?.top_products?.length || 0,
      icon: Package,
      iconColor: 'orange',
      sub: 'Top sản phẩm',
    },
  ];

  return (
    <div>
      {/* Impersonation banner */}
      {impersonatedTenant && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: '#fffbeb', border: '1px solid #fcd34d',
          borderRadius: 10, padding: '10px 14px', marginBottom: 20,
        }}>
          <Eye size={16} style={{ color: '#d97706' }} />
          <span style={{ fontSize: 13, color: '#92400e', fontWeight: 500 }}>
            Đang xem dashboard của tenant <strong>{impersonatedTenant}</strong>
          </span>
          <span style={{ fontSize: 12, color: '#b45309' }}>
            (SuperAdmin impersonation)
          </span>
        </div>
      )}

      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>
            <TrendingUp size={24} style={{ color: '#3b82f6' }} />
            Dashboard
          </h1>
          <p>Tổng quan dữ liệu kinh doanh</p>
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={loadData}
          style={{ marginTop: 4 }}
        >
          <RefreshCw size={14} />
          Làm mới
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="card" style={{ marginBottom: 20, borderLeft: '4px solid #dc2626' }}>
          <div className="card-body" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <AlertCircle size={20} style={{ color: '#dc2626' }} />
            <div>
              <p style={{ fontWeight: 600, color: '#dc2626' }}>{error}</p>
              <p style={{ fontSize: 12, color: '#94a3b8' }}>Nhấn "Làm mới" để thử lại</p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="stats-grid stagger-children">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="stat-card" style={{ animationDelay: `${i * 80}ms` }}>
              {loading ? (
                <>
                  <div className="skeleton" style={{ width: 42, height: 42, borderRadius: 10, marginBottom: 14 }} />
                  <div className="skeleton" style={{ width: '60%', height: 12, marginBottom: 8 }} />
                  <div className="skeleton" style={{ width: '80%', height: 28 }} />
                </>
              ) : (
                <>
                  <div className={`stat-icon ${card.iconColor}`}>
                    <Icon size={20} />
                  </div>
                  <div className="stat-label">{card.label}</div>
                  <div className="stat-value">{card.value}</div>
                  <div className="stat-sub">{card.sub}</div>
                </>
              )}
            </div>
          );
        })}
      </div>

      {/* Monthly Revenue */}
      {loading ? (
        <div className="card">
          <div className="card-header">
            <h3><TrendingUp size={16} />Doanh thu theo tháng</h3>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Tháng</th><th>Doanh thu</th><th>Lợi nhuận</th><th>Số đơn</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3].map((i) => (
                  <tr key={i}>
                    <td><div className="skeleton" style={{ width: 60, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 100, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 80, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 50, height: 20, borderRadius: 999 }} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : summary?.monthly?.length > 0 ? (
        <div className="card">
          <div className="card-header">
            <h3><TrendingUp size={16} />Doanh thu theo tháng (12 tháng gần nhất)</h3>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Tháng</th>
                  <th>Doanh thu</th>
                  <th>Lợi nhuận</th>
                  <th>Số đơn</th>
                </tr>
              </thead>
              <tbody>
                {summary.monthly.map((row) => (
                  <tr key={`${row.year}-${row.month}`}>
                    <td><span style={{ fontWeight: 600, color: '#0f172a' }}>{String(row.month).padStart(2, '0')}/{row.year}</span></td>
                    <td style={{ color: '#059669', fontWeight: 600 }}>{row.revenue.toLocaleString('vi-VN')}đ</td>
                    <td>{row.profit.toLocaleString('vi-VN')}đ</td>
                    <td><span className="badge badge-info">{row.orders.toLocaleString()}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {/* Store Performance */}
      {loading ? (
        <div className="card">
          <div className="card-header">
            <h3><TrendingUp size={16} />Top cửa hàng theo doanh thu</h3>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Cửa hàng</th><th>Thành phố</th><th>Doanh thu</th><th>Số đơn</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3].map((i) => (
                  <tr key={i}>
                    <td><div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div className="skeleton" style={{ width: 28, height: 28, borderRadius: '50%' }} />
                      <div className="skeleton" style={{ width: 120, height: 16 }} />
                    </div></td>
                    <td><div className="skeleton" style={{ width: 80, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 100, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 50, height: 20, borderRadius: 999 }} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : summary?.stores?.length > 0 ? (
        <div className="card">
          <div className="card-header">
            <h3><TrendingUp size={16} />Top cửa hàng theo doanh thu</h3>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Cửa hàng</th>
                  <th>Thành phố</th>
                  <th>Doanh thu</th>
                  <th>Số đơn</th>
                </tr>
              </thead>
              <tbody>
                {summary.stores.map((row, i) => (
                  <tr key={row.store_name}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{
                          width: 28, height: 28, borderRadius: '50%',
                          background: i === 0 ? '#fef3c7' : i === 1 ? '#f1f5f9' : '#f1f5f9',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: 12, fontWeight: 700,
                          color: i === 0 ? '#d97706' : '#64748b',
                        }}>{i + 1}</div>
                        <span style={{ fontWeight: 500 }}>{row.store_name}</span>
                      </div>
                    </td>
                    <td style={{ color: '#64748b' }}>{row.city}</td>
                    <td style={{ color: '#059669', fontWeight: 600 }}>{row.revenue.toLocaleString('vi-VN')}đ</td>
                    <td><span className="badge badge-default">{row.orders.toLocaleString()}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {/* Top Products */}
      {loading ? (
        <div className="card">
          <div className="card-header">
            <h3><Package size={16} />Top sản phẩm bán chạy</h3>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th><th>Tên sản phẩm</th><th>Danh mục</th><th>Số lượng</th><th>Doanh thu</th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3].map((i) => (
                  <tr key={i}>
                    <td><div className="skeleton" style={{ width: 24, height: 24, borderRadius: '50%' }} /></td>
                    <td><div className="skeleton" style={{ width: 160, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 80, height: 20, borderRadius: 999 }} /></td>
                    <td><div className="skeleton" style={{ width: 60, height: 16 }} /></td>
                    <td><div className="skeleton" style={{ width: 100, height: 16 }} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : stats?.top_products?.length > 0 ? (
        <div className="card">
          <div className="card-header">
            <h3><Package size={16} />Top sản phẩm bán chạy</h3>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Tên sản phẩm</th>
                  <th>Danh mục</th>
                  <th>Số lượng</th>
                  <th>Doanh thu</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_products.map((p, i) => (
                  <tr key={p.product_name}>
                    <td>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                        width: 24, height: 24, borderRadius: '50%',
                        fontSize: 12, fontWeight: 700,
                        background: i < 3 ? ['#fef3c7', '#f1f5f9', '#fdf2f8'][i] : '#f1f5f9',
                        color: i < 3 ? ['#d97706', '#64748b', '#db2777'][i] : '#64748b',
                      }}>{i + 1}</span>
                    </td>
                    <td style={{ fontWeight: 500 }}>{p.product_name}</td>
                    <td><span className="badge badge-purple">{p.category}</span></td>
                    <td>{p.total_qty?.toLocaleString()}</td>
                    <td style={{ color: '#059669', fontWeight: 600 }}>{p.total_revenue?.toLocaleString('vi-VN')}đ</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {/* Empty state - only show when not loading and no data */}
      {!loading && !error && !stats && (
        <div className="card">
          <div className="empty-state">
            <TrendingUp size={48} style={{ color: '#cbd5e1' }} />
            <p style={{ marginTop: 12, fontWeight: 500 }}>Chưa có dữ liệu</p>
            <p style={{ marginTop: 4, fontSize: 13, color: '#94a3b8' }}>
              Hãy chạy ETL để nạp dữ liệu vào data warehouse
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
