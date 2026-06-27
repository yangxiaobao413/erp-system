from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Customer, Product, Order, OrderStatus
from app.schemas import ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["经营看板"])


@router.get("/stats", summary="经营数据看板", description="返回客户数量、产品数量、累计销售额、待处理订单数")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = current_user.company_id

    customer_count = (await db.execute(
        select(func.count()).select_from(
            select(Customer).where(Customer.company_id == company_id, Customer.is_deleted == False).subquery()
        )
    )).scalar()

    product_count = (await db.execute(
        select(func.count()).select_from(
            select(Product).where(Product.company_id == company_id, Product.is_deleted == False).subquery()
        )
    )).scalar()

    total_sales = (await db.execute(
        select(func.coalesce(func.sum(Order.total_amount), 0)).where(
            Order.company_id == company_id,
            Order.is_deleted == False,
            Order.status == OrderStatus.COMPLETED,
        )
    )).scalar() or 0

    pending_orders = (await db.execute(
        select(func.count()).where(
            Order.company_id == company_id,
            Order.is_deleted == False,
            Order.status == OrderStatus.PENDING,
        )
    )).scalar()

    return ResponseModel(data={
        "customer_count": customer_count,
        "product_count": product_count,
        "total_sales": float(total_sales),
        "pending_orders": pending_orders,
    })
