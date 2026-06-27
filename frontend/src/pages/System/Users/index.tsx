import { useRef } from 'react';
import { ProTable, ModalForm, ProFormText, ProFormSelect } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { Button, message, Popconfirm, Tag, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const UserManagement: React.FC = () => {
  const actionRef = useRef<ActionType>();

  const columns: ProColumns<any>[] = [
    { title: 'ID', dataIndex: 'id', width: 60, search: false },
    { title: '用户名', dataIndex: 'username' },
    { title: '工号', dataIndex: 'employee_no', search: false },
    { title: '姓名', dataIndex: 'full_name' },
    { title: '部门', dataIndex: 'department' },
    {
      title: '状态', dataIndex: 'status', width: 80,
      render: (_, r) => r.status === 'active'
        ? <Tag color="green">启用</Tag>
        : <Tag color="red">禁用</Tag>,
    },
    { title: '创建时间', dataIndex: 'created_at', valueType: 'dateTime', search: false, width: 160 },
    {
      title: '操作', valueType: 'option', width: 240,
      render: (_, record) => [
        <Popconfirm key="toggle" title={`确定${record.status === 'active' ? '禁用' : '启用'}该用户？`}
          onConfirm={async () => {
            const token = localStorage.getItem('token');
            const newStatus = record.status === 'active' ? 'disabled' : 'active';
            const res = await fetch(`/api/admin/users/${record.id}/status`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
              body: JSON.stringify({ status: newStatus }),
            });
            const data = await res.json();
            if (data.code === 200) message.success(data.message);
            else message.error(data.message);
            actionRef.current?.reload();
          }}
        >
          <Button type="link" size="small">{record.status === 'active' ? '禁用' : '启用'}</Button>
        </Popconfirm>,
        <Popconfirm key="reset" title="确定重置密码为 123456？"
          onConfirm={async () => {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/admin/users/${record.id}/reset-password`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
              body: JSON.stringify({ new_password: '123456' }),
            });
            const data = await res.json();
            if (data.code === 200) message.success(data.message);
            else message.error(data.message);
          }}
        >
          <Button type="link" size="small">重置密码</Button>
        </Popconfirm>,
      ],
    },
  ];

  return (
    <ProTable<any>
      headerTitle="用户列表"
      actionRef={actionRef}
      rowKey="id"
      search={{ labelWidth: 'auto' }}
      request={async (params) => {
        const token = localStorage.getItem('token');
        const query = new URLSearchParams();
        query.set('page', String(params.current || 1));
        query.set('page_size', String(params.pageSize || 20));
        if (params.username) query.set('keyword', params.username);
        if (params.status) query.set('status', params.status);
        const res = await fetch(`/api/admin/users?${query}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        return { data: data.data?.list || [], total: data.data?.total || 0, success: true };
      }}
      columns={columns}
      toolBarRender={() => [
        <ModalForm<any>
          key="add" title="新增用户" trigger={<Button type="primary"><PlusOutlined /> 新增用户</Button>}
          modalProps={{ destroyOnClose: true }}
          onFinish={async (values) => {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/admin/users', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
              body: JSON.stringify(values),
            });
            const data = await res.json();
            if (data.code === 200) {
              message.success('用户创建成功，初始密码: ' + (values.password || ''));
              actionRef.current?.reload();
              return true;
            }
            message.error(data.message || '创建失败');
            return false;
          }}
        >
          <ProFormText name="username" label="用户名" rules={[{ required: true }]} />
          <ProFormText name="password" label="初始密码" rules={[{ required: true, min: 6 }]} />
          <ProFormText name="employee_no" label="工号" />
          <ProFormText name="full_name" label="姓名" />
          <ProFormText name="department" label="部门" />
          <ProFormText name="email" label="邮箱" />
          <ProFormText name="phone" label="电话" />
        </ModalForm>,
      ]}
    />
  );
};

export default UserManagement;
