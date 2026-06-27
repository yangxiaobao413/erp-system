import { useState } from 'react';
import { Form, Input, Button, message, Card } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';

const ChangePasswordPage: React.FC = () => {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: any) => {
    if (values.new_password !== values.confirm_password) {
      message.error('两次密码不一致');
      return;
    }
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          old_password: values.old_password,
          new_password: values.new_password,
        }),
      });
      const data = await res.json();
      if (data.code === 200) {
        message.success('密码修改成功');
        history.push('/dashboard');
      } else {
        message.error(data.message || '修改失败');
      }
    } catch (err: any) {
      message.error(err.message || '修改失败');
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
        <h2 style={{ textAlign: 'center', marginBottom: 24 }}>修改密码</h2>
        <p style={{ textAlign: 'center', color: '#999', marginBottom: 24 }}>
          首次登录需要修改密码
        </p>
        <Form onFinish={handleSubmit} size="large">
          <Form.Item name="old_password" rules={[{ required: true, message: '请输入原密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="原密码" />
          </Form.Item>
          <Form.Item name="new_password" rules={[{ required: true, min: 6, message: '新密码至少6位' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="新密码" />
          </Form.Item>
          <Form.Item name="confirm_password" rules={[{ required: true, message: '请确认新密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="确认新密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              确认修改
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default ChangePasswordPage;
