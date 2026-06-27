import { useState } from 'react';
import { Form, Input, Button, message, Card } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { history, useModel } from '@umijs/max';

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { refresh } = useModel('@@initialState');

  const handleLogin = async (values: API.LoginParams) => {
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      const data = await res.json();
      if (data.code === 200 && data.data) {
        localStorage.setItem('token', data.data.access_token);
        localStorage.setItem('refresh_token', data.data.refresh_token);
        localStorage.setItem('user', JSON.stringify(data.data.user));

        if (data.data.must_change_password) {
          message.info('首次登录，请修改密码');
          history.push('/user/change-password');
        } else {
          message.success(data.message || '登录成功');
          await refresh();
          history.push('/dashboard');
        }
      } else {
        message.error(data.message || '登录失败');
      }
    } catch (err: any) {
      message.error(err.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      minHeight: '100vh', background: '#f0f2f5'
    }}>
      <Card style={{ width: 400, boxShadow: '0 2px 8px rgba(0,0,0,0.15)' }}>
        <h2 style={{ textAlign: 'center', marginBottom: 32 }}>ERP 管理系统</h2>
        <Form onFinish={handleLogin} size="large">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
