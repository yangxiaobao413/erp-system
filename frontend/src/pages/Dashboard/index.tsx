import { useEffect, useState } from 'react';
import { Card, Statistic, Row, Col, Spin } from 'antd';
import {
  TeamOutlined,
  ShoppingOutlined,
  DollarOutlined,
  FileTextOutlined,
} from '@ant-design/icons';

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<API.DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/dashboard/stats', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.code === 200) {
        setStats(data.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="客户总数"
              value={stats?.customer_count || 0}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="产品总数"
              value={stats?.product_count || 0}
              prefix={<ShoppingOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总销售额"
              value={stats?.total_sales || 0}
              prefix={<DollarOutlined />}
              precision={2}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理订单"
              value={stats?.pending_orders || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: stats?.pending_orders ? '#cf1322' : undefined }}
            />
          </Card>
        </Col>
      </Row>
      <Card title="欢迎使用 ERP 管理系统">
        <p>这是一个轻量级企业资源管理系统，您可以在此管理客户、产品和订单。</p>
      </Card>
    </div>
  );
};

export default DashboardPage;
