import { defineConfig } from '@umijs/max';

export default defineConfig({
  antd: {},
  access: {},
  model: {},
  initialState: {},
  request: {},
  layout: {
    title: 'ERP 管理系统',
  },
  routes: [
    {
      path: '/user',
      layout: false,
      routes: [
        { name: '登录', path: '/user/login', component: './User/Login' },
        { name: '修改密码', path: '/user/change-password', component: './User/ChangePassword' },
      ],
    },
    { path: '/', redirect: '/dashboard' },
    { name: '工作台', access: 'isLoggedIn', path: '/dashboard', component: './Dashboard', icon: 'DashboardOutlined' },
    { name: '客户管理', access: 'isLoggedIn', path: '/customer', component: './Customer', icon: 'TeamOutlined' },
    { name: '产品管理', access: 'isLoggedIn', path: '/product', component: './Product', icon: 'ShoppingOutlined' },
    {
      name: '订单管理', access: 'isLoggedIn', path: '/order', icon: 'FileTextOutlined',
      routes: [
        { name: '订单列表', path: '/order/list', component: './Order/List' },
        { name: '创建订单', path: '/order/create', component: './Order/Create' },
      ],
    },
    { name: '系统管理', access: 'isLoggedIn', path: '/system', icon: 'SettingOutlined',
      routes: [
        { name: '用户管理', path: '/system/users', component: './System/Users' },
      ],
    },
  ],
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
  npmClient: 'npm',
});
