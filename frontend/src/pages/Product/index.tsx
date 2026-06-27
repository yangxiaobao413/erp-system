import { useRef } from 'react';
import { ProTable, ModalForm, ProFormText, ProFormDigit, ProFormTextArea, ProFormSelect } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { Button, message, Popconfirm, Tag } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const ProductPage: React.FC = () => {
  const actionRef = useRef<ActionType>();

  const columns: ProColumns<API.ProductItem>[] = [
    { title: 'ID', dataIndex: 'id', width: 60, search: false },
    { title: '产品名称', dataIndex: 'name', ellipsis: true },
    { title: '产品编码', dataIndex: 'code' },
    { title: '分类', dataIndex: 'category' },
    { title: '单位', dataIndex: 'unit', width: 60, search: false },
    {
      title: '售价',
      dataIndex: 'price',
      valueType: 'money',
      search: false,
      width: 100,
    },
    {
      title: '成本',
      dataIndex: 'cost',
      valueType: 'money',
      search: false,
      width: 100,
    },
    {
      title: '库存',
      dataIndex: 'stock',
      search: false,
      width: 80,
      render: (_, record) => {
        const isLow = record.stock <= record.low_stock_threshold;
        return (
          <Tag color={isLow ? 'red' : 'green'}>
            {record.stock}
            {isLow ? ' (低库存)' : ''}
          </Tag>
        );
      },
    },
    {
      title: '预警阈值',
      dataIndex: 'low_stock_threshold',
      search: false,
      width: 100,
    },
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
        <ModalForm<API.ProductItem>
          key="edit"
          title="编辑产品"
          trigger={<Button type="link" size="small">编辑</Button>}
          modalProps={{ destroyOnClose: true }}
          onFinish={async (values) => {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/products/${record.id}`, {
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
          <ProFormText name="name" label="产品名称" rules={[{ required: true }]} initialValue={record.name} />
          <ProFormText name="code" label="产品编码" initialValue={record.code} />
          <ProFormText name="category" label="分类" initialValue={record.category} />
          <ProFormText name="unit" label="单位" initialValue={record.unit} />
          <ProFormDigit name="price" label="售价" min={0} initialValue={record.price} />
          <ProFormDigit name="cost" label="成本" min={0} initialValue={record.cost} />
          <ProFormDigit name="stock" label="库存" min={0} initialValue={record.stock} />
          <ProFormDigit name="low_stock_threshold" label="预警阈值" min={0} initialValue={record.low_stock_threshold} />
          <ProFormTextArea name="description" label="描述" initialValue={record.description} />
        </ModalForm>,
        <Popconfirm
          key="delete"
          title="确定删除该产品？"
          onConfirm={async () => {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/products/${record.id}`, {
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
    <ProTable<API.ProductItem>
      headerTitle="产品列表"
      actionRef={actionRef}
      rowKey="id"
      search={{ labelWidth: 'auto' }}
      rowClassName={(record) => (record.stock <= record.low_stock_threshold ? 'low-stock-row' : '')}
      request={async (params) => {
        const token = localStorage.getItem('token');
        const query = new URLSearchParams();
        query.set('page', String(params.current || 1));
        query.set('page_size', String(params.pageSize || 20));
        if (params.name) query.set('keyword', params.name);
        if (params.category) query.set('category', params.category);
        const res = await fetch(`/api/products?${query}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        return { data: data.data?.list || [], total: data.data?.total || 0, success: true };
      }}
      columns={columns}
      toolBarRender={() => [
        <ModalForm<API.ProductItem>
          key="add"
          title="新增产品"
          trigger={
            <Button type="primary">
              <PlusOutlined /> 新增产品
            </Button>
          }
          modalProps={{ destroyOnClose: true }}
          onFinish={async (values) => {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/products', {
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
          <ProFormText name="name" label="产品名称" rules={[{ required: true }]} />
          <ProFormText name="code" label="产品编码" />
          <ProFormText name="category" label="分类" />
          <ProFormText name="unit" label="单位" initialValue="个" />
          <ProFormDigit name="price" label="售价" min={0} rules={[{ required: true }]} initialValue={0} />
          <ProFormDigit name="cost" label="成本" min={0} initialValue={0} />
          <ProFormDigit name="stock" label="库存" min={0} initialValue={0} />
          <ProFormDigit name="low_stock_threshold" label="预警阈值" min={0} initialValue={10} />
          <ProFormTextArea name="description" label="描述" />
        </ModalForm>,
      ]}
    />
  );
};

export default ProductPage;
