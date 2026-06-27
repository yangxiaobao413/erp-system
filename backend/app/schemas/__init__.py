from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models import OrderStatus, UserStatus


# ── Common ──
class ResponseModel(BaseModel):
    code: int = 200
    data: Optional[dict | list] = None
    message: str = "success"


# ═══════════════════ Auth ─────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    must_change_password: bool = False
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ═══════════════════ Admin / User ─────────
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    employee_no: Optional[str] = None
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    role_ids: Optional[List[int]] = None


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    employee_no: Optional[str] = None
    role_ids: Optional[List[int]] = None


class UserStatusRequest(BaseModel):
    status: UserStatus


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    username: str
    employee_no: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    status: UserStatus
    must_change_password: bool
    company_id: int
    roles: list = []
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════ Role ─────────────────
class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    menu_ids: Optional[List[int]] = None


class RoleOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    menus: list = []

    class Config:
        from_attributes = True


# ═══════════════════ Menu ─────────────────
class MenuOut(BaseModel):
    id: int
    parent_id: Optional[int] = None
    name: str
    code: str
    type: str
    path: Optional[str] = None
    icon: Optional[str] = None
    sort_order: int
    children: list = []

    class Config:
        from_attributes = True


# ═══════════════════ Customer ─────────────
class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════ Product ──────────────
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = None
    category: Optional[str] = None
    unit: str = "个"
    price: float = Field(..., ge=0)
    cost: float = Field(0.0, ge=0)
    stock: int = Field(0, ge=0)
    low_stock_threshold: int = Field(10, ge=0)
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    stock: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    description: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    unit: str
    price: float
    cost: float
    stock: int
    low_stock_threshold: int
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════ Order ────────────────
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    remark: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class DashboardStats(BaseModel):
    customer_count: int
    product_count: int
    total_sales: float
    pending_orders: int

class OrderOut(BaseModel):
    id: int; order_no: str; customer_id: int; customer_name: Optional[str] = None
    total_amount: float; status: OrderStatus; remark: Optional[str] = None
    items: list = []; created_at: datetime; updated_at: datetime
    class Config: from_attributes = True