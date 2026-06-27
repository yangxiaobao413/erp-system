import { RequestConfig, RunTimeLayoutConfig, history } from '@umijs/max';
import { message, Button, Dropdown, Avatar, Space } from 'antd';
import { UserOutlined, LogoutOutlined, KeyOutlined } from '@ant-design/icons';

// 刷新 token
async function refreshAccessToken(): Promise<string | null> {
  const rt = localStorage.getItem('refresh_token');
  if (!rt) return null;
  try {
    const res = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: rt }),
    });
    if (res.ok) {
      const data = await res.json();
      if (data.code === 200 && data.data) {
        localStorage.setItem('token', data.data.access_token);
        localStorage.setItem('refresh_token', data.data.refresh_token);
        return data.data.access_token;
      }
    }
  } catch {}
  return null;
}

let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

export const request: RequestConfig = {
  timeout: 30000,
  errorConfig: {
    errorHandler(error: any) {
      if (error?.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        history.push('/user/login');
      }
    },
  },
  requestInterceptors: [
    (url: string, options: any) => {
      const token = localStorage.getItem('token');
      const headers: Record<string, string> = { ...options.headers };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      return { url, options: { ...options, headers } };
    },
  ],
  responseInterceptors: [
    async (response: any) => {
      if (response.status === 401 && !response.url.includes('/api/auth/refresh')) {
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = refreshAccessToken();
        }
        const newToken = await refreshPromise;
        isRefreshing = false;
        refreshPromise = null;
        if (newToken) {
          const newHeaders = { ...response.config.headers, Authorization: `Bearer ${newToken}` };
          return fetch(response.config.url, { ...response.config, headers: newHeaders });
        }
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        history.push('/user/login');
      }
      return response;
    },
  ],
};

export async function getInitialState(): Promise<{
  currentUser?: API.CurrentUser;
  menuData?: any[];
}> {
  const token = localStorage.getItem('token');
  if (!token) return {};

  try {
    const res = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      const user = data.data;
      localStorage.setItem('user', JSON.stringify(user));

      // 获取动态菜单
      let menus: any[] = [];
      try {
        const menuRes = await fetch('/api/admin/menus/tree', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (menuRes.ok) {
          const menuData = await menuRes.json();
          menus = menuData.data || [];
        }
      } catch {}

      return { currentUser: user, menuData: menus };
    }
  } catch {}

  return {};
}

export const layout: RunTimeLayoutConfig = ({ initialState }) => {
  const user = initialState?.currentUser;
  return {
    title: 'ERP 管理系统',
    logo: 'https://img.alicdn.com/tfs/TB1YHEpwUT1gK0jSZFrXXcNCXXa-28-28.svg',
    menu: { locale: false, defaultOpenAll: true },
    onPageChange: () => {
      const token = localStorage.getItem('token');
      if (!token && window.location.pathname !== '/user/login' && !window.location.pathname.startsWith('/user/change-password')) {
        window.location.href = '/user/login';
      }
    },
    unAccessible: (
      <div style={{ textAlign: 'center', paddingTop: 100 }}>
        <h2>请先登录</h2>
        <Button type="primary" onClick={() => window.location.href = '/user/login'}>去登录</Button>
      </div>
    ),
    logout: () => {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      window.location.href = '/user/login';
    },
    rightContentRender: () => user ? (
      <Space>
        <Dropdown menu={{
          items: [
            { key: 'change-pwd', icon: <KeyOutlined />, label: '修改密码',
              onClick: () => history.push('/user/change-password') },
            { key: 'logout', icon: <LogoutOutlined />, label: '退出登录',
              onClick: () => {
                localStorage.removeItem('token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                window.location.href = '/user/login';
              }},
          ],
        }}>
          <Space style={{ cursor: 'pointer' }}>
            <Avatar size="small" icon={<UserOutlined />} />
            <span>{user.full_name || user.username}</span>
          </Space>
        </Dropdown>
      </Space>
    ) : null,
  };
};
