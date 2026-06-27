import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum as SAEnum, Table
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


# ── RBAC 关联表 ──
user_role = Table(
    "user_role", Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_menu = Table(
    "role_menu", Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("menu_id", Integer, ForeignKey("menus.id"), primary_key=True),
)


# ── 公司 ──
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    users = relationship("User", back_populates="company")


# ── 用户（扩展） ──
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    employee_no = Column(String(50), nullable=True, index=True)        # 工号
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)                     # 部门
    status = Column(SAEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)  # 启用/禁用
    must_change_password = Column(Boolean, default=True, nullable=False)  # 首次登录标记
    refresh_token = Column(String(500), nullable=True)                  # 刷新令牌
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    company = relationship("Company", back_populates="users")
    roles = relationship("Role", secondary=user_role, back_populates="users")


# ── 角色 ──
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, index=True)  # admin / manager / user
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    users = relationship("User", secondary=user_role, back_populates="roles")
    menus = relationship("Menu", secondary=role_menu, back_populates="roles")


# ── 菜单/权限 ──
class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True)
    name = Column(String(100), nullable=False)           # 菜单名称
    code = Column(String(100), nullable=False, index=True) # 权限标识 eg: customer:list
    type = Column(String(20), default="menu")             # menu / button
    path = Column(String(200), nullable=True)              # 前端路由
    icon = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    children = relationship("Menu", backref="parent", remote_side=[id])
    roles = relationship("Role", secondary=role_menu, back_populates="menus")


# ── 客户 ──
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(200), nullable=True)
    address = Column(String(500), nullable=True)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    orders = relationship("Order", back_populates="customer")


# ── 产品 ──
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True)
    unit = Column(String(50), default="个", nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    cost = Column(Float, default=0.0, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=10, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    order_items = relationship("OrderItem", back_populates="product")


# ── 订单 ──
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    order_no = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# ── 订单明细 ──
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
