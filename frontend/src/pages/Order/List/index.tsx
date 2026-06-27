import { useRef } from 'react';
import { ProTable } from '@ant-design/pro-components';
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { Button, message, Popconfirm, Tag, Modal, Descriptions, Space } from 'antd';
import { history } from '@umijs/max';
import { PlusOutlined } from '@ant-design/icons';

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待处理' },
  confirmed: { color: 'blue', text: '已确认' },
  shipped: { color: 'orange', text: '已发货' },
  completed: { color: 'green', text: '已完成' },
  cancelled: { color: 'red', text: '已取消' },
};

const OrderListPage: React.FC = () => {
  const actionRef = useRef<ActionType>();

  const handleStatusChange = async (orderId: number, newStatus: string) => {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/orders/${orderId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status: newStatus }),
    });
    const data = await res.json();
    if (data.code === 200) {
      message.success('状态更新成功');
      actionRef.current?.reload();
    } else {
      message.error(data.message || '更新失败');
    }
  };

  const columns: ProColumns<API.OrderRecord>[] = [
    { title: 'ID', dataIndex: 'id', width: 60, search: false },
    { title: '订单号', dataIndex: 'order_no', width: 200, copyable: true },
    { title: '客户', dataIndex: 'customer_name', search: false },
    {
      title: '金额',
      dataIndex: 'total_amount',
      valueType: 'money',
      search: false,
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (_, record) => {
        const s = statusMap[record.status] || { color: 'default', text: record.status };
        return <Tag color={s.color}>{s.text}</Tag>;
      },
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
      width: 320,
      render: (_, record) => [
        <Button
          key="detail"
          type="link"
          size="small"
          onClick={() => {
            Modal.info({
              title: `订单详情 - ${record.order_no}`,
              width: 600,
              content: (
                <Descriptions column={1} size="small" style={{ marginTop: 16 }}>
                  <Descriptions.Item label="客户">{record.customer_name}</Descriptions.Item>
                  <Descriptions.Item label="状态">
                    <Tag color={statusMap[record.status]?.color}>{statusMap[record.status]?.text}</Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="总金额">¥{record.total_amount.toFixed(2)}</Descriptions.Item>
                  <Descriptions.Item label="备注">{record.remark || '-'}</Descriptions.Item>
                  <Descriptions.Item label="商品明细">
                    {record.items?.map((item) => (
                      <div key={item.id}>
                        {item.product_name} × {item.quantity} = ¥{item.subtotal.toFixed(2)}
                      </div>
                    )) || '-'}
                  </Descriptions.Item>
                </Descriptions>
              ),
            });
          }}
        >
          详情
        </Button>,
        record.status === 'pending' && (
          <Popconfirm key="confirm" title="确认该订单？" onConfirm={() => handleStatusChange(record.id, 'confirmed')}>
            <Button type="link" size="small" style={{ color: '#1677ff' }}>确认</Button>
          </Popconfirm>
        ),
        record.status === 'confirmed' && (
          <Popconfirm key="ship" title="标记为已发货？" onConfirm={() => handleStatusChange(record.id, 'shipped')}>
            <Button type="link" size="small" style={{ color: '#fa8c16' }}>发货</Button>
          </Popconfirm>
        ),
        record.status === 'shipped' && (
          <Popconfirm key="complete" title="标记为已完成？" onConfirm={() => handleStatusChange(record.id, 'completed')}>
            <Button type="link" size="small" style={{ color: '#52c41a' }}>完成</Button>
          </Popconfirm>
        ),
        (record.status === 'pending' || record.status === 'confirmed') && (
          <Popconfirm key="cancel" title="取消该订单？库存将归还" onConfirm={() => handleStatusChange(record.id, 'cancelled')}>
            <Button type="link" size="small" danger>取消</Button>
          </Popconfirm>
        ),
      ].filter(Boolean),
    },
  ];

  return (
    <ProTable<API.OrderRecord>
      headerTitle="订单列表"
      actionRef={actionRef}
      rowKey="id"
      search={{ labelWidth: 'auto' }}
      request={async (params) => {
        const token = localStorage.getItem('token');
        const query = new URLSearchParams();
        query.set('page', String(params.current || 1));
        query.set('page_size', String(params.pageSize || 20));
        if (params.status) query.set('status', params.status);
        if (params.order_no) query.set('keyword', params.order_no);
        const res = await fetch(`/api/orders?${query}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        return { data: data.data?.list || [], total: data.data?.total || 0, success: true };
      }}
      columns={columns}
      toolBarRender={() => [
        <Button
          key="create"
          type="primary"
          onClick={() => history.push('/order/create')}
        >
          <PlusOutlined /> 创建订单
        </Button>,
      ]}
    />
  );
};

export default OrderListPage;
