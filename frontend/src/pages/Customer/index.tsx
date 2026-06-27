import { useRef } from 'react';
import { ProTable, ModalForm, ProFormText, ProFormTextArea } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { Button, message, Popconfirm } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const CustomerPage: React.FC = () => {
  const actionRef = useRef<ActionType>();

  const columns: ProColumns<API.CustomerItem>[] = [
    { title: 'ID', dataIndex: 'id', width: 60, search: false },
    { title: '客户名称', dataIndex: 'name', ellipsis: true },
    { title: '联系人', dataIndex: 'contact_person', search: false },
    { title: '电话', dataIndex: 'phone', search: false },
    { title: '邮箱', dataIndex: 'email', search: false },
    { title: '地址', dataIndex: 'address', search: false, ellipsis: true },
    { title: '备注', dataIndex: 'remark', search: false, ellipsis: true },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      valueType: 'dateTime',
      search: false,
      width: 160,
    },
    {
      title: '操作',
      valueType: 'option',
      width: 160,
      render: (_, record) => [
        <ModalForm<API.CustomerItem>
          key="edit"
          title="编辑客户"
          trigger={<Button type="link" size="small">编辑</Button>}
          modalProps={{ destroyOnClose: true }}
          onFinish={async (values) => {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/customers/${record.id}`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
              body: JSON.stringify(values),
            });
            const data = await res.json();
            if (data.code === 200) {
              message.success('更新成功');
              actionRef.current?.reload();
              return true;
            }
            message.error(data.message || '更新失败');
            return false;
          }}
        >
          <ProFormText name="name" label="客户名称" rules={[{ required: true }]} initialValue={record.name} />
          <ProFormText name="contact_person" label="联系人" initialValue={record.contact_person} />
          <ProFormText name="phone" label="电话" initialValue={record.phone} />
          <ProFormText name="email" label="邮箱" initialValue={record.email} />
          <ProFormText name="address" label="地址" initialValue={record.address} />
          <ProFormTextArea name="remark" label="备注" initialValue={record.remark} />
        </ModalForm>,
        <Popconfirm
          key="delete"
          title="确定删除该客户？"
          onConfirm={async () => {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/customers/${record.id}`, {
              method: 'DELETE',
              headers: { Authorization: `Bearer ${token}` },
            });
            const data = await res.json();
            if (data.code === 200) {
              message.success('删除成功');
              actionRef.current?.reload();
            } else {
              message.error(data.message || '删除失败');
            }
          }}
        >
          <Button type="link" size="small" danger>删除</Button>
        </Popconfirm>,
      ],
    },
  ];

  return (
    <ProTable<API.CustomerItem>
      headerTitle="客户列表"
      actionRef={actionRef}
      rowKey="id"
      search={{ labelWidth: 'auto' }}
      request={async (params) => {
        const token = localStorage.getItem('token');
        const query = new URLSearchParams();
        query.set('page', String(params.current || 1));
        query.set('page_size', String(params.pageSize || 20));
        if (params.name) query.set('keyword', params.name);
        const res = await fetch(`/api/customers?${query}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        return { data: data.data?.list || [], total: data.data?.total || 0, success: true };
      }}
      columns={columns}
      toolBarRender={() => [
        <ModalForm<API.CustomerItem>
          key="add"
          title="新增客户"
          trigger={
            <Button type="primary">
              <PlusOutlined /> 新增客户
            </Button>
          }
          modalProps={{ destroyOnClose: true }}
          onFinish={async (values) => {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/customers', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
              body: JSON.stringify(values),
            });
            const data = await res.json();
            if (data.code === 200) {
              message.success('创建成功');
              actionRef.current?.reload();
              return true;
            }
            message.error(data.message || '创建失败');
            return false;
          }}
        >
          <ProFormText name="name" label="客户名称" rules={[{ required: true }]} />
          <ProFormText name="contact_person" label="联系人" />
          <ProFormText name="phone" label="电话" />
          <ProFormText name="email" label="邮箱" />
          <ProFormText name="address" label="地址" />
          <ProFormTextArea name="remark" label="备注" />
        </ModalForm>,
      ]}
    />
  );
};

export default CustomerPage;
