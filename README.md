# ERP 管理系统

企业级轻量 ERP 系统，支持客户管理、产品管理、订单管理和经营数据分析。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + PostgreSQL |
| 前端 | React + UmiJS + Ant Design |
| 认证 | JWT 双令牌 + BCrypt + RBAC 权限 |

## 快速启动

### 1. 启动数据库

```bash
docker compose up -d db
```

或确保本地 PostgreSQL 运行在 `localhost:5432`，建库：

```sql
CREATE USER erp_user WITH PASSWORD 'erp_password';
CREATE DATABASE erp_db OWNER erp_user;
```

### 2. 启动后端

```bash
cd backend
cp .env.example .env    # 修改数据库密码等配置
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端页面：http://localhost:8001

### 4. 首次使用

1. 打开 http://localhost:8001 ，注册管理员账号
2. 登录后进入工作台，开始管理客户、产品、订单

## 项目结构

```
ERP系统dk/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 应用入口
│   │   ├── models.py      # 数据库模型（RBAC）
│   │   ├── auth.py        # JWT 认证 & 权限
│   │   ├── routers/       # API 路由
│   │   │   ├── auth.py        # 登录/改密/刷新令牌
│   │   │   ├── admin.py       # 账号管理
│   │   │   ├── customers.py   # 客户 CRUD
│   │   │   ├── products.py    # 产品 CRUD
│   │   │   ├── orders.py      # 订单管理
│   │   │   └── dashboard.py   # 经营看板
│   │   └── schemas/       # 数据模型
│   ├── requirements.txt
│   └── .env.example
├── frontend/          # React 前端
│   ├── src/pages/
│   │   ├── Dashboard/     # 工作台
│   │   ├── Customer/      # 客户管理
│   │   ├── Product/       # 产品管理
│   │   ├── Order/         # 订单管理
│   │   ├── System/        # 系统管理（用户/角色）
│   │   └── User/          # 登录/改密
│   ├── .umirc.ts
│   └── package.json
├── docker-compose.yml # Docker 编排
└── README.md
```

## 功能特性

- **JWT 双令牌认证**：Access Token + Refresh Token，自动续期
- **RBAC 权限模型**：用户 → 角色 → 菜单，管理员可分配权限
- **首次登录改密**：管理员创建账号后，用户首次登录强制修改密码
- **库存自动管理**：创建订单自动扣库存，取消订单自动归还
- **低库存预警**：低于阈值时自动标记
- **软删除**：删除操作可恢复
