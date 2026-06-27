import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Order, OrderItem, Product, Customer, OrderStatus
from app.schemas import OrderCreate, OrderOut, OrderItemOut, OrderStatusUpdate, ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["订单业务"])


def _generate_order_no() -> str:
    return f"ORD{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"


@router.get("", summary="查询订单列表", description="可按订单状态和订单号搜索")
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base = select(Order).where(Order.company_id == current_user.company_id, Order.is_deleted == False)
    if status:
        base = base.where(Order.status == status)
    if keyword:
        base = base.where(Order.order_no.ilike(f"%{keyword}%"))

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar()

    rows = (await db.execute(
        base.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size)
    )).scalars().all()

    items = []
    for order in rows:
        cust_result = await db.execute(select(Customer).where(Customer.id == order.customer_id))
        customer = cust_result.scalar_one_or_none()
        items_result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id, OrderItem.is_deleted == False)
        )
        order_items = items_result.scalars().all()
        item_outs = []
        for oi in order_items:
            prod_result = await db.execute(select(Product).where(Product.id == oi.product_id))
            prod = prod_result.scalar_one_or_none()
            item_outs.append(OrderItemOut(
                id=oi.id,
                product_id=oi.product_id,
                product_name=prod.name if prod else "",
                quantity=oi.quantity,
                unit_price=oi.unit_price,
                subtotal=oi.subtotal,
            ).model_dump(mode="json"))

        items.append({
            "id": order.id,
            "order_no": order.order_no,
            "customer_id": order.customer_id,
            "customer_name": customer.name if customer else "",
            "total_amount": order.total_amount,
            "status": order.status.value,
            "remark": order.remark,
            "items": item_outs,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat(),
        })

    return ResponseModel(data={"list": items, "total": total, "page": page, "page_size": page_size})


@router.post("", summary="创建订单", description="选择客户和产品，系统自动扣减库存、计算金额")
async def create_order(
    req: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    customer_result = await db.execute(
        select(Customer).where(Customer.id == req.customer_id, Customer.company_id == current_user.company_id, Customer.is_deleted == False)
    )
    customer = customer_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    order = Order(
        company_id=current_user.company_id,
        order_no=_generate_order_no(),
        customer_id=req.customer_id,
        total_amount=0,
        status=OrderStatus.PENDING,
        remark=req.remark,
    )
    db.add(order)
    await db.flush()

    total_amount = 0
    for item_req in req.items:
        prod_result = await db.execute(
            select(Product).where(Product.id == item_req.product_id, Product.company_id == current_user.company_id, Product.is_deleted == False)
        )
        product = prod_result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"产品ID {item_req.product_id} 不存在")
        if product.stock < item_req.quantity:
            raise HTTPException(status_code=400, detail=f"产品「{product.name}」库存不足，当前库存：{product.stock}")

        product.stock -= item_req.quantity
        subtotal = round(product.price * item_req.quantity, 2)
        total_amount += subtotal

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_req.quantity,
            unit_price=product.price,
            subtotal=subtotal,
        )
        db.add(order_item)

    order.total_amount = round(total_amount, 2)
    await db.flush()

    items_result = await db.execute(
        select(OrderItem).where(OrderItem.order_id == order.id, OrderItem.is_deleted == False)
    )
    order_items = items_result.scalars().all()
    item_outs = []
    for oi in order_items:
        prod_result2 = await db.execute(select(Product).where(Product.id == oi.product_id))
        prod2 = prod_result2.scalar_one_or_none()
        item_outs.append(OrderItemOut(
            id=oi.id,
            product_id=oi.product_id,
            product_name=prod2.name if prod2 else "",
            quantity=oi.quantity,
            unit_price=oi.unit_price,
            subtotal=oi.subtotal,
        ).model_dump(mode="json"))

    return ResponseModel(data={
        "id": order.id,
        "order_no": order.order_no,
        "customer_id": order.customer_id,
        "customer_name": customer.name,
        "total_amount": order.total_amount,
        "status": order.status.value,
        "remark": order.remark,
        "items": item_outs,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }, message="订单创建成功")


@router.get("/{order_id}", summary="查看订单详情", description="查看订单的客户、商品明细和金额")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.company_id == current_user.company_id, Order.is_deleted == False)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    cust_result = await db.execute(select(Customer).where(Customer.id == order.customer_id))
    customer = cust_result.scalar_one_or_none()

    items_result = await db.execute(
        select(OrderItem).where(OrderItem.order_id == order.id, OrderItem.is_deleted == False)
    )
    order_items = items_result.scalars().all()
    item_outs = []
    for oi in order_items:
        prod_result = await db.execute(select(Product).where(Product.id == oi.product_id))
        prod = prod_result.scalar_one_or_none()
        item_outs.append(OrderItemOut(
            id=oi.id,
            product_id=oi.product_id,
            product_name=prod.name if prod else "",
            quantity=oi.quantity,
            unit_price=oi.unit_price,
            subtotal=oi.subtotal,
        ).model_dump(mode="json"))

    return ResponseModel(data={
        "id": order.id,
        "order_no": order.order_no,
        "customer_id": order.customer_id,
        "customer_name": customer.name if customer else "",
        "total_amount": order.total_amount,
        "status": order.status.value,
        "remark": order.remark,
        "items": item_outs,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    })


@router.put("/{order_id}/status", summary="变更订单状态", description="确认→发货→完成；取消时会自动归还库存")
async def update_order_status(
    order_id: int,
    req: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.company_id == current_user.company_id, Order.is_deleted == False)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    old_status = order.status
    order.status = req.status

    if req.status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
        items_result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id, OrderItem.is_deleted == False)
        )
        for oi in items_result.scalars().all():
            prod_result = await db.execute(
                select(Product).where(Product.id == oi.product_id, Product.is_deleted == False)
            )
            product = prod_result.scalar_one_or_none()
            if product:
                product.stock += oi.quantity

    await db.flush()
    return ResponseModel(message="状态更新成功")


@router.delete("/{order_id}", summary="删除订单", description="仅待处理状态的订单可删除，库存自动归还")
async def delete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.company_id == current_user.company_id, Order.is_deleted == False)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status == OrderStatus.PENDING:
        items_result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order.id, OrderItem.is_deleted == False)
        )
        for oi in items_result.scalars().all():
            prod_result = await db.execute(
                select(Product).where(Product.id == oi.product_id, Product.is_deleted == False)
            )
            product = prod_result.scalar_one_or_none()
            if product:
                product.stock += oi.quantity

    order.is_deleted = True
    await db.flush()
    return ResponseModel(message="删除成功")
