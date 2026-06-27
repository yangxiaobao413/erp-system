from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.database import get_db
from app.models import User, Customer
from app.schemas import CustomerCreate, CustomerUpdate, CustomerOut, ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/customers", tags=["客户业务"])


@router.get("", summary="查询客户列表", description="支持按姓名、电话、联系人搜索，可翻页浏览")
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base = select(Customer).where(Customer.company_id == current_user.company_id, Customer.is_deleted == False)
    if keyword:
        base = base.where(
            or_(
                Customer.name.ilike(f"%{keyword}%"),
                Customer.contact_person.ilike(f"%{keyword}%"),
                Customer.phone.ilike(f"%{keyword}%"),
            )
        )
    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar()

    rows = (await db.execute(base.order_by(Customer.id.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    items = [CustomerOut.model_validate(c).model_dump(mode="json") for c in rows]

    return ResponseModel(data={"list": items, "total": total, "page": page, "page_size": page_size})


@router.post("", summary="新增客户", description="录入一个新客户的基本信息")
async def create_customer(
    req: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    customer = Customer(company_id=current_user.company_id, **req.model_dump())
    db.add(customer)
    await db.flush()
    return ResponseModel(data=CustomerOut.model_validate(customer).model_dump(mode="json"), message="创建成功")


@router.get("/{customer_id}", summary="查看客户详情", description="查看某个客户的完整信息")
async def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.company_id == current_user.company_id, Customer.is_deleted == False)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return ResponseModel(data=CustomerOut.model_validate(customer).model_dump(mode="json"))


@router.put("/{customer_id}", summary="编辑客户", description="修改客户的联系方式或备注")
async def update_customer(
    customer_id: int,
    req: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.company_id == current_user.company_id, Customer.is_deleted == False)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(customer, k, v)
    await db.flush()
    return ResponseModel(data=CustomerOut.model_validate(customer).model_dump(mode="json"), message="更新成功")


@router.delete("/{customer_id}", summary="删除客户", description="删除后可在后台恢复")
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.company_id == current_user.company_id, Customer.is_deleted == False)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    customer.is_deleted = True
    await db.flush()
    return ResponseModel(message="删除成功")
