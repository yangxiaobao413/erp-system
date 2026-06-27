declare namespace API {
  type CurrentUser = {
    id: number;
    username: string;
    full_name?: string;
    email?: string;
    company_id: number;
    company_name?: string;
  };

  type LoginParams = {
    username: string;
    password: string;
  };

  type RegisterParams = {
    username: string;
    password: string;
    full_name?: string;
    email?: string;
    company_name: string;
  };

  type CustomerItem = {
    id: number;
    name: string;
    contact_person?: string;
    phone?: string;
    email?: string;
    address?: string;
    remark?: string;
    created_at: string;
    updated_at: string;
  };

  type ProductItem = {
    id: number;
    name: string;
    code?: string;
    category?: string;
    unit: string;
    price: number;
    cost: number;
    stock: number;
    low_stock_threshold: number;
    description?: string;
    created_at: string;
    updated_at: string;
  };

  type OrderItem = {
    id: number;
    product_id: number;
    product_name?: string;
    quantity: number;
    unit_price: number;
    subtotal: number;
  };

  type OrderItem2 = {
    product_id: number;
    quantity: number;
  };

  type OrderRecord = {
    id: number;
    order_no: string;
    customer_id: number;
    customer_name?: string;
    total_amount: number;
    status: string;
    remark?: string;
    items: OrderItem[];
    created_at: string;
    updated_at: string;
  };

  type DashboardStats = {
    customer_count: number;
    product_count: number;
    total_sales: number;
    pending_orders: number;
  };

  type ApiResponse<T = any> = {
    code: number;
    data: T;
    message: string;
  };
}
