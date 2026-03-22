import React, { useState, useEffect } from 'react';
import { getStats, getSummary } from '../services/api';

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
      <div className="loading">
        <div className="spinner"></div>
        Đang tải dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-msg">{error}</div>
        <button className="btn btn-primary" onClick={loadData}>Thử lại</button>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Tổng quan dữ liệu kinh doanh</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="label">Tổng doanh thu</div>
          <div className="value">{stats?.total_revenue?.toLocaleString('vi-VN')}đ</div>
          <div className="sub">Từ FactSales</div>
        </div>
        <div className="stat-card">
          <div className="label">Tổng đơn hàng</div>
          <div className="value">{stats?.total_orders?.toLocaleString()}</div>
          <div className="sub">Hóa đơn bán hàng</div>
        </div>
        <div className="stat-card">
          <div className="label">Tổng khách hàng</div>
          <div className="value">{stats?.total_customers?.toLocaleString()}</div>
          <div className="sub">Trong DimCustomer</div>
        </div>
        <div className="stat-card">
          <div className="label">Top sản phẩm</div>
          <div className="value">{stats?.top_products?.length || 0}</div>
          <div className="sub">Sản phẩm được theo dõi</div>
        </div>
      </div>

      {summary?.monthly?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3>Doanh thu theo tháng (12 tháng gần nhất)</h3>
          </div>
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
                  <td>{row.month}/{row.year}</td>
                  <td>{row.revenue.toLocaleString('vi-VN')}đ</td>
                  <td>{row.profit.toLocaleString('vi-VN')}đ</td>
                  <td>{row.orders.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {summary?.stores?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3>Top cửa hàng theo doanh thu</h3>
          </div>
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
              {summary.stores.map((row) => (
                <tr key={row.store_name}>
                  <td>{row.store_name}</td>
                  <td>{row.city}</td>
                  <td>{row.revenue.toLocaleString('vi-VN')}đ</td>
                  <td>{row.orders.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {stats?.top_products?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3>Top sản phẩm bán chạy</h3>
          </div>
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
                  <td>{i + 1}</td>
                  <td>{p.product_name}</td>
                  <td>{p.category}</td>
                  <td>{p.total_qty?.toLocaleString()}</td>
                  <td>{p.total_revenue?.toLocaleString('vi-VN')}đ</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!stats && (
        <div className="empty-state">
          <p>Chưa có dữ liệu. Hãy chạy ETL để nạp dữ liệu.</p>
        </div>
      )}
    </div>
  );
}
