# ERP 管理系统后端使用手册

## 目录
1. [系统概述](#系统概述)
2. [快速开始](#快速开始)
3. [账户模块](#账户模块)
4. [客户业务](#客户业务)
5. [产品业务](#产品业务)
6. [订单业务](#订单业务)
7. [经营看板](#经营看板)
8. [账号管理](#账号管理)
9. [常见问题](#常见问题)

---

## 系统概述

本系统是一套轻量级企业资源管理（ERP）后端 API，提供客户管理、产品管理、订单管理和经营数据看板功能。采用 JWT 令牌认证，支持 RBAC 角色权限控制。

- **技术栈**：FastAPI + PostgreSQL
- **API 文档**：http://localhost:8000/docs
- **API 地址**：http://localhost:8000

### 统一响应格式

所有接口返回格式统一为：

```json
{
  "code": 200,
  "data": { ... },
  "message": "success"
}
```

- `code=200` 表示成功，其他值表示错误
- `data` 为具体返回数据
- `message` 为提示信息

---

## 快速开始

### 第一步：获取 Token

打开 http://localhost:8000/docs ，找到 **"账户"** 分组下的 `POST /api/auth/login`，点 "试用"，输入：

```json
{
  "username": "yangxiaobao",
  "password": "88888888"
}
```

点 "执行"，复制返回结果中的 `access_token`。

### 第二步：授权

点页面右上角 🔒 **"授权"** 按钮，在 Value 框中粘贴：

```
Bearer eyJhbGci...你的access_token...
```

（注意 Bearer 后面有一个空格）

点 "授权" → "关闭"，看到 🔒 旁出现 ✅ 即成功。此后所有接口均可正常调用。

### 如果你的 Token 过期

Token 有效期为 24 小时。过期后重新执行第一步和第二步即可。刷新页面不会丢失授权（已配置持久化）。

---

## 账户模块

### 登录

```
POST /api/auth/login
```

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例：**
```json
{
  "username": "yangxiaobao",
  "password": "88888888"
}
```

**返回字段说明：**
| 字段 | 说明 |
|------|------|
| access_token | 访问令牌，调用其他接口时使用 |
| refresh_token | 刷新令牌，用于自动续期（前端处理） |
| must_change_password | 是否首次登录需改密（true=需要） |
| user.id | 用户ID |
| user.username | 用户名 |
| user.full_name | 姓名 |
| user.employee_no | 工号 |
| user.department | 部门 |
| user.company_name | 公司名称 |

### 修改密码

```
POST /api/auth/change-password
```

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码（至少6位） |

**请求示例：**
```json
{
  "old_password": "88888888",
  "new_password": "新密码123456"
}
```

### 查看个人信息

```
GET /api/auth/me
```

无需参数，返回当前登录用户的完整信息，包括角色和权限列表。

---

## 客户业务

### 查询客户列表

```
GET /api/customers
```

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | 数字 | 否 | 1 | 页码 |
| page_size | 数字 | 否 | 20 | 每页条数（最大100） |
| keyword | 字符串 | 否 | - | 按姓名/电话/联系人搜索 |

**使用示例：**
- 查第1页：`/api/customers?page=1&page_size=20`
- 搜索"华为"：`/api/customers?keyword=华为`

**返回字段：**
| 字段 | 说明 |
|------|------|
| list | 客户列表 |
| total | 总条数 |
| page | 当前页码 |
| page_size | 每页条数 |

**客户对象字段：**
| 字段 | 说明 |
|------|------|
| id | 客户ID |
| name | 客户名称 |
| contact_person | 联系人 |
| phone | 电话 |
| email | 邮箱 |
| address | 地址 |
| remark | 备注 |
| created_at | 创建时间 |

### 新增客户

```
POST /api/customers
```

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 客户名称 |
| contact_person | string | 否 | 联系人 |
| phone | string | 否 | 电话 |
| email | string | 否 | 邮箱 |
| address | string | 否 | 地址 |
| remark | string | 否 | 备注 |

**请求示例：**
```json
{
  "name": "深圳科技有限公司",
  "contact_person": "王经理",
  "phone": "13800138000"
}
```

### 查看客户详情

```
GET /api/customers/{customer_id}
```

将 `{customer_id}` 替换为具体的客户ID，如 `/api/customers/1`

### 编辑客户

```
PUT /api/customers/{customer_id}
```

参数与新增相同，只需填写要修改的字段。

**请求示例：**
```json
{
  "phone": "13900139000",
  "address": "深圳市南山区"
}
```

### 删除客户

```
DELETE /api/customers/{customer_id}
```

无需请求体。删除为软删除，数据仍保留在数据库中。

---

## 产品业务

### 查询产品列表

```
GET /api/products
```

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | 数字 | 否 | 页码，默认1 |
| page_size | 数字 | 否 | 每页条数，默认20 |
| keyword | 字符串 | 否 | 按产品名称/编码搜索 |
| category | 字符串 | 否 | 按分类筛选 |
| low_stock | 布尔 | 否 | true=只看低库存产品 |

**使用示例：**
- 看硬件类产品：`/api/products?category=硬件`
- 看库存不足的：`/api/products?low_stock=true`

**产品对象字段：**
| 字段 | 说明 |
|------|------|
| id | 产品ID |
| name | 产品名称 |
| code | 产品编码 |
| category | 分类 |
| unit | 单位（个/箱/台等） |
| price | 售价 |
| cost | 成本 |
| stock | 当前库存 |
| low_stock_threshold | 库存预警阈值 |
| description | 描述 |
| created_at | 创建时间 |

### 新增产品

```
POST /api/products
```

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 产品名称 |
| code | string | 否 | 产品编码 |
| category | string | 否 | 分类（如：硬件、软件、耗材） |
| unit | string | 否 | 单位，默认"个" |
| price | 数字 | 是 | 售价（≥0） |
| cost | 数字 | 否 | 成本，默认0 |
| stock | 数字 | 否 | 库存数量，默认0 |
| low_stock_threshold | 数字 | 否 | 预警阈值，默认10 |
| description | string | 否 | 描述 |

**请求示例：**
```json
{
  "name": "服务器主机",
  "code": "SRV-001",
  "category": "硬件",
  "unit": "台",
  "price": 50000,
  "cost": 35000,
  "stock": 20,
  "low_stock_threshold": 5
}
```

### 查看产品详情

```
GET /api/products/{product_id}
```

### 编辑产品

```
PUT /api/products/{product_id}
```

只填要修改的字段即可。

**请求示例（只修改价格和库存）：**
```json
{
  "price": 48000,
  "stock": 15
}
```

### 删除产品

```
DELETE /api/products/{product_id}
```

### 查看产品分类列表

```
GET /api/products/categories/list
```

返回已有的所有产品分类名称。

---

## 订单业务

### 订单状态说明

| 状态值 | 中文 | 说明 |
|--------|------|------|
| pending | 待处理 | 新建订单的初始状态 |
| confirmed | 已确认 | 确认订单有效 |
| shipped | 已发货 | 商品已出库 |
| completed | 已完成 | 订单完结，计入销售额 |
| cancelled | 已取消 | 订单取消，库存自动归还 |

### 查询订单列表

```
GET /api/orders
```

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | 数字 | 否 | 页码 |
| page_size | 数字 | 否 | 每页条数 |
| status | 字符串 | 否 | 按状态筛选：pending/confirmed/shipped/completed/cancelled |
| keyword | 字符串 | 否 | 按订单号搜索 |

**使用示例：**
- 查看待处理订单：`/api/orders?status=pending`

**订单对象字段：**
| 字段 | 说明 |
|------|------|
| id | 订单ID |
| order_no | 订单编号 |
| customer_id | 客户ID |
| customer_name | 客户名称 |
| total_amount | 订单总金额 |
| status | 订单状态 |
| remark | 备注 |
| items | 商品明细列表 |
| created_at | 创建时间 |

### 创建订单

```
POST /api/orders
```

> ⚠️ 创建订单会自动扣减产品库存，库存不足时创建失败。

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | 数字 | 是 | 客户ID |
| items | 数组 | 是 | 商品明细 |
| remark | string | 否 | 备注 |

items 数组中每个元素：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_id | 数字 | 是 | 产品ID |
| quantity | 数字 | 是 | 购买数量（>0） |

**请求示例：**
```json
{
  "customer_id": 1,
  "remark": "加急处理",
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 3, "quantity": 5 }
  ]
}
```

### 查看订单详情

```
GET /api/orders/{order_id}
```

返回订单完整信息，含客户信息和商品明细。

### 变更订单状态

```
PUT /api/orders/{order_id}/status
```

> ⚠️ 将订单设为 "cancelled" 时，系统会自动归还库存。

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 是 | 目标状态 |

**状态流转规则：**
```
待处理(pending) → 已确认(confirmed) → 已发货(shipped) → 已完成(completed)
                                                    ↘ 已取消(cancelled) ← 待处理/已确认
```

**请求示例：**
```json
{
  "status": "confirmed"
}
```

### 删除订单

```
DELETE /api/orders/{order_id}
```

仅待处理(pending)状态的订单可删除，删除时自动归还库存。

---

## 经营看板

### 获取经营数据

```
GET /api/dashboard/stats
```

返回当前公司的核心经营指标：

```json
{
  "code": 200,
  "data": {
    "customer_count": 3,    // 客户总数
    "product_count": 4,     // 产品总数
    "total_sales": 49000.0, // 累计销售额（仅统计"已完成"订单）
    "pending_orders": 2     // 待处理订单数
  }
}
```

---

## 账号管理

> 📌 此模块仅管理员可见

### 查看账号列表

```
GET /api/admin/users
```

**请求参数：**
| 参数 | 说明 |
|------|------|
| page | 页码 |
| page_size | 每页条数 |
| keyword | 按用户名/姓名搜索 |
| status | 按状态筛选：active=启用, disabled=禁用 |

### 新建账号

```
POST /api/admin/users
```

> 📌 管理员新建的账号首次登录必须修改密码。

**请求参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名（3-100字符） |
| password | string | 是 | 初始密码（至少6位） |
| employee_no | string | 否 | 工号 |
| full_name | string | 否 | 姓名 |
| email | string | 否 | 邮箱 |
| phone | string | 否 | 电话 |
| department | string | 否 | 部门 |

**请求示例：**
```json
{
  "username": "zhangsan",
  "password": "123456",
  "employee_no": "EMP002",
  "full_name": "张三",
  "department": "销售部"
}
```

### 编辑账号信息

```
PUT /api/admin/users/{user_id}
```

修改员工姓名、部门、工号等基本信息（不含密码）。

### 启用/停用账号

```
PUT /api/admin/users/{user_id}/status
```

**请求示例：**
```json
{ "status": "disabled" }
```

停用后该账号无法登录。可随时重新启用。

### 重置密码

```
PUT /api/admin/users/{user_id}/reset-password
```

**请求示例：**
```json
{ "new_password": "新密码123" }
```

重置后用户下次登录必须修改密码。

---

## 常见问题

**Q: 提示"令牌无效或已过期"怎么办？**
A: 重新执行登录接口获取新 Token，然后点右上角"授权"更新。Token 有效期为24小时。

**Q: 提示"权限不足"？**
A: 当前账号的角色没有该接口的操作权限，联系管理员分配权限。

**Q: 创建订单提示"库存不足"？**
A: 检查该产品的当前库存，可以先通过"编辑产品"接口增加库存。

**Q: 删除客户/产品后还能恢复吗？**
A: 系统采用软删除，数据仍在数据库中。目前没有恢复接口，但数据不会丢失。

**Q: 如何添加新员工账号？**
A: 用管理员账号登录，在 Swagger 的"账号管理"中使用 `POST /api/admin/users` 创建。

---

> 完整接口文档随时可访问：http://localhost:8000/docs
