from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.database import get_db
from app.models import User, Product
from app.schemas import ProductCreate, ProductUpdate, ProductOut, ResponseModel
from app.auth import get_current_user

router = APIRouter(prefix="/api/products", tags=["产品业务"])


@router.get("", summary="查询产品列表", description="可搜索产品名称/编码、按分类或低库存筛选")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    low_stock: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base = select(Product).where(Product.company_id == current_user.company_id, Product.is_deleted == False)
    if keyword:
        base = base.where(
            or_(Product.name.ilike(f"%{keyword}%"), Product.code.ilike(f"%{keyword}%"))
        )
    if category:
        base = base.where(Product.category == category)
    if low_stock:
        base = base.where(Product.stock <= Product.low_stock_threshold)

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar()

    rows = (await db.execute(base.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    items = [ProductOut.model_validate(p).model_dump(mode="json") for p in rows]

    return ResponseModel(data={"list": items, "total": total, "page": page, "page_size": page_size})


@router.post("", summary="新增产品", description="录入产品信息，含售价、成本、库存、预警阈值")
async def create_product(
    req: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    product = Product(company_id=current_user.company_id, **req.model_dump())
    db.add(product)
    await db.flush()
    return ResponseModel(data=ProductOut.model_validate(product).model_dump(mode="json"), message="创建成功")


@router.get("/{product_id}", summary="查看产品详情", description="查看某个产品的完整信息")
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.company_id == current_user.company_id, Product.is_deleted == False)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return ResponseModel(data=ProductOut.model_validate(product).model_dump(mode="json"))


@router.put("/{product_id}", summary="编辑产品", description="修改产品价格、库存等信息")
async def update_product(
    product_id: int,
    req: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.company_id == current_user.company_id, Product.is_deleted == False)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(product, k, v)
    await db.flush()
    return ResponseModel(data=ProductOut.model_validate(product).model_dump(mode="json"), message="更新成功")


@router.delete("/{product_id}", summary="删除产品", description="删除产品（软删除）")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.company_id == current_user.company_id, Product.is_deleted == False)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    product.is_deleted = True
    await db.flush()
    return ResponseModel(message="删除成功")


@router.get("/categories/list", summary="查看产品分类", description="列出当前所有产品的分类名称")
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product.category).where(
            Product.company_id == current_user.company_id,
            Product.is_deleted == False,
            Product.category.isnot(None),
        ).distinct()
    )
    categories = [r for r in result.scalars().all() if r]
    return ResponseModel(data=categories)
