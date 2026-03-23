import React, { useState, useEffect } from 'react';
import { getStats, getSummary } from '../services/api';
import {
  TrendingUp,
  ShoppingCart,
  Users,
  Package,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
} from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
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

  if (loading) {
    return (
      <div>
        <div className="page-header">
          <h1>
            <TrendingUp size={24} style={{ color: '#3b82f6' }} />
            Dashboard
          </h1>
          <p>Tổng quan dữ liệu kinh doanh</p>
        </div>
        <div className="stats-grid stagger-children">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="stat-card" style={{ opacity: 0.5 }}>
              <div className="skeleton" style={{ width: 42, height: 42, borderRadius: 10, marginBottom: 14 }} />
              <div className="skeleton" style={{ width: '60%', height: 12, marginBottom: 8 }} />
              <div className="skeleton" style={{ width: '80%', height: 28 }} />
            </div>
          ))}
        </div>
        <div className="card">
          <div className="skeleton" style={{ width: '40%', height: 16, margin: '20px 24px 12px' }} />
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton" style={{ width: '90%', height: 48, margin: '4px 24px' }} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-header">
        <h1>
          <TrendingUp size={24} style={{ color: '#3b82f6' }} />
          Dashboard
        </h1>
      </div>
    );
  }

  const statCards = [
    {
      label: 'Tổng doanh thu',
      value: stats?.total_revenue?.toLocaleString('vi-VN') + 'đ' || '0đ',
      icon: TrendingUp,
      iconColor: 'blue',
      sub: 'Từ FactSales',
      trend: null,
    },
    {
      label: 'Tổng đơn hàng',
      value: stats?.total_orders?.toLocaleString() || '0',
      icon: ShoppingCart,
      iconColor: 'green',
      sub: 'Hóa đơn bán hàng',
      trend: null,
    },
    {
      label: 'Tổng khách hàng',
      value: stats?.total_customers?.toLocaleString() || '0',
      icon: Users,
      iconColor: 'purple',
      sub: 'Trong DimCustomer',
      trend: null,
    },
    {
      label: 'Sản phẩm theo dõi',
      value: stats?.top_products?.length || 0,
      icon: Package,
      iconColor: 'orange',
      sub: 'Top sản phẩm',
      trend: null,
    },
  ];

  return (
    <div>
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

      {/* Stats Grid */}
      <div className="stats-grid stagger-children">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="stat-card" style={{ animationDelay: `${i * 80}ms` }}>
              <div className={`stat-icon ${card.iconColor}`}>
                <Icon size={20} />
              </div>
              <div className="stat-label">{card.label}</div>
              <div className="stat-value">{card.value}</div>
              <div className="stat-sub">{card.sub}</div>
              {card.trend && (
                <div className={`stat-trend ${card.trend.dir}`}>
                  {card.trend.dir === 'up' ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                  {card.trend.value}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Monthly Revenue */}
      {summary?.monthly?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3>
              <TrendingUp size={16} />
              Doanh thu theo tháng (12 tháng gần nhất)
            </h3>
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
                    <td>
                      <span style={{ fontWeight: 600, color: '#0f172a' }}>
                        {String(row.month).padStart(2, '0')}/{row.year}
                      </span>
                    </td>
                    <td style={{ color: '#059669', fontWeight: 600 }}>
                      {row.revenue.toLocaleString('vi-VN')}đ
                    </td>
                    <td style={{ color: '#0f172a' }}>
                      {row.profit.toLocaleString('vi-VN')}đ
                    </td>
                    <td>
                      <span className="badge badge-info">{row.orders.toLocaleString()}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Store Performance */}
      {summary?.stores?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3>
              <TrendingUp size={16} />
              Top cửa hàng theo doanh thu
            </h3>
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
                          width: 28,
                          height: 28,
                          borderRadius: '50%',
                          background: i === 0 ? '#fef3c7' : i === 1 ? '#f1f5f9' : i === 2 ? '#fef3c7' : '#f1f5f9',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: 12,
                          fontWeight: 700,
                          color: i === 0 ? '#d97706' : '#64748b',
                        }}>
                          {i + 1}
                        </div>
                        <span style={{ fontWeight: 500 }}>{row.store_name}</span>
                      </div>
                    </td>
                    <td style={{ color: '#64748b' }}>{row.city}</td>
                    <td style={{ color: '#059669', fontWeight: 600 }}>
                      {row.revenue.toLocaleString('vi-VN')}đ
                    </td>
                    <td>
                      <span className="badge badge-default">{row.orders.toLocaleString()}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top Products */}
      {stats?.top_products?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3>
              <Package size={16} />
              Top sản phẩm bán chạy
            </h3>
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
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        fontSize: 12,
                        fontWeight: 700,
                        background: i < 3 ? ['#fef3c7', '#f1f5f9', '#fdf2f8'][i] : '#f1f5f9',
                        color: i < 3 ? ['#d97706', '#64748b', '#db2777'][i] : '#64748b',
                      }}>
                        {i + 1}
                      </span>
                    </td>
                    <td style={{ fontWeight: 500 }}>{p.product_name}</td>
                    <td>
                      <span className="badge badge-purple">{p.category}</span>
                    </td>
                    <td>{p.total_qty?.toLocaleString()}</td>
                    <td style={{ color: '#059669', fontWeight: 600 }}>
                      {p.total_revenue?.toLocaleString('vi-VN')}đ
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!stats && (
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
