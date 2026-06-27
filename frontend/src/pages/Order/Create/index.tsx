import { useState, useEffect } from 'react';
import { Card, Form, Select, Button, InputNumber, Table, message, Input, Space, Popconfirm } from 'antd';
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';

interface OrderItemDraft {
  key: string;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

const OrderCreatePage: React.FC = () => {
  const [form] = Form.useForm();
  const [customers, setCustomers] = useState<API.CustomerItem[]>([]);
  const [products, setProducts] = useState<API.ProductItem[]>([]);
  const [items, setItems] = useState<OrderItemDraft[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const token = localStorage.getItem('token') || '';

  useEffect(() => {
    fetchCustomers();
    fetchProducts();
  }, []);

  const fetchCustomers = async () => {
    const res = await fetch('/api/customers?page=1&page_size=999', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (data.code === 200) setCustomers(data.data.list);
  };

  const fetchProducts = async () => {
    const res = await fetch('/api/products?page=1&page_size=999', {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (data.code === 200) setProducts(data.data.list);
  };

  const addItem = () => {
    setItems([
      ...items,
      { key: Date.now().toString(), product_id: 0, product_name: '', quantity: 1, unit_price: 0, subtotal: 0 },
    ]);
  };

  const removeItem = (key: string) => {
    setItems(items.filter((item) => item.key !== key));
  };

  const updateItem = (key: string, field: string, value: any) => {
    setItems((prev) =>
      prev.map((item) => {
        if (item.key !== key) return item;
        const updated = { ...item, [field]: value };
        if (field === 'product_id') {
          const prod = products.find((p) => p.id === value);
          if (prod) {
            updated.product_name = prod.name;
            updated.unit_price = prod.price;
            updated.subtotal = +(prod.price * updated.quantity).toFixed(2);
          }
        }
        if (field === 'quantity') {
          updated.subtotal = +(updated.unit_price * value).toFixed(2);
        }
        return updated;
      })
    );
  };

  const totalAmount = items.reduce((sum, item) => sum + item.subtotal, 0);

  const handleSubmit = async () => {
    const values = await form.validateFields();
    if (items.length === 0) {
      message.error('请至少添加一个产品');
      return;
    }
    const invalidItem = items.find((i) => i.product_id === 0);
    if (invalidItem) {
      message.error('请为每个产品选择具体产品');
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          customer_id: values.customer_id,
          remark: values.remark,
          items: items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
        }),
      });
      const data = await res.json();
      if (data.code === 200) {
        message.success('订单创建成功');
        history.push('/order/list');
      } else {
        message.error(data.message || '创建失败');
      }
    } catch (err: any) {
      message.error(err.message || '创建失败');
    } finally {
      setSubmitting(false);
    }
  };

  const itemColumns = [
    {
      title: '产品',
      dataIndex: 'product_id',
      width: 250,
      render: (_: any, record: OrderItemDraft) => (
        <Select
          showSearch
          style={{ width: '100%' }}
          placeholder="选择产品"
          value={record.product_id || undefined}
          onChange={(val) => updateItem(record.key, 'product_id', val)}
          filterOption={(input, option) =>
            (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
          }
          options={products.map((p) => ({ label: `${p.name} (库存:${p.stock})`, value: p.id }))}
        />
      ),
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      width: 120,
      render: (_: any, record: OrderItemDraft) => (
        <InputNumber
          min={1}
          value={record.quantity}
          onChange={(val) => updateItem(record.key, 'quantity', val || 1)}
        />
      ),
    },
    {
      title: '单价',
      dataIndex: 'unit_price',
      width: 120,
      render: (_: any, record: OrderItemDraft) => `¥${record.unit_price}`,
    },
    {
      title: '小计',
      dataIndex: 'subtotal',
      width: 120,
      render: (_: any, record: OrderItemDraft) => `¥${record.unit_price}`,
    },
    {
      title: '操作',
      width: 80,
      render: (_: any, record: OrderItemDraft) => (
        <Popconfirm title="删除该项？" onConfirm={() => removeItem(record.key)}>
          <Button type="link" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <Card title="创建订单">
      <Form form={form} layout="vertical" style={{ maxWidth: 800 }}>
        <Form.Item
          name="customer_id"
          label="选择客户"
          rules={[{ required: true, message: '请选择客户' }]}
        >
          <Select
            showSearch
            placeholder="搜索并选择客户"
            filterOption={(input, option) =>
              (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
            }
            options={customers.map((c) => ({ label: c.name, value: c.id }))}
          />
        </Form.Item>
        <Form.Item name="remark" label="备注">
          <Input.TextArea rows={2} />
        </Form.Item>

        <div style={{ marginBottom: 16 }}>
          <Space style={{ marginBottom: 12 }}>
            <Button type="dashed" onClick={addItem} icon={<PlusOutlined />}>
              添加产品
            </Button>
          </Space>
          <Table
            rowKey="key"
            columns={itemColumns}
            dataSource={items}
            pagination={false}
            size="small"
            summary={() => (
              <Table.Summary.Row>
                <Table.Summary.Cell index={0} colSpan={3}>
                  <strong>合计</strong>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={1}>
                  <strong>¥{totalAmount.toFixed(2)}</strong>
                </Table.Summary.Cell>
                <Table.Summary.Cell index={2} />
              </Table.Summary.Row>
            )}
          />
        </div>

        <Form.Item>
          <Space>
            <Button type="primary" onClick={handleSubmit} loading={submitting}>
              提交订单
            </Button>
            <Button onClick={() => history.push('/order/list')}>取消</Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default OrderCreatePage;
