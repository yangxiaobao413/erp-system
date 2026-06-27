from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import User, Role, Menu, UserStatus
from app.schemas import (
    UserCreateRequest, UserUpdateRequest, UserStatusRequest,
    ResetPasswordRequest, UserOut, RoleCreate, RoleOut, MenuOut, ResponseModel,
)
from app.auth import hash_password, get_current_user, require_admin

router = APIRouter(prefix="/api/admin", tags=["账号管理"])


# ═══════════════════ 用户管理 ═══════════════════

@router.get("/users", summary="账号列表", description="查看所有员工账号，支持搜索和状态筛选", dependencies=[Depends(require_admin())])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base = select(User).options(selectinload(User.roles)).where(
        User.company_id == current_user.company_id, User.is_deleted == False
    )
    if keyword:
        base = base.where(
            User.username.ilike(f"%{keyword}%") | User.full_name.ilike(f"%{keyword}%")
        )
    if status:
        base = base.where(User.status == status)

    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar()

    rows = (await db.execute(
        base.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
    )).scalars().all()

    items = []
    for u in rows:
        items.append({
            "id": u.id, "username": u.username, "employee_no": u.employee_no,
            "full_name": u.full_name, "email": u.email, "phone": u.phone,
            "department": u.department, "status": u.status.value,
            "must_change_password": u.must_change_password,
            "company_id": u.company_id,
            "roles": [{"id": r.id, "name": r.name, "code": r.code} for r in u.roles],
            "created_at": u.created_at.isoformat(),
        })
    return ResponseModel(data={"list": items, "total": total, "page": page, "page_size": page_size})


@router.post("/users", summary="新建账号", description="为新员工创建账号，默认首次登录需修改密码", dependencies=[Depends(require_admin())])
async def create_user(
    req: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(User).where(User.username == req.username, User.is_deleted == False)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        company_id=current_user.company_id,
        username=req.username,
        employee_no=req.employee_no,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        email=req.email,
        phone=req.phone,
        department=req.department,
        must_change_password=True,  # 管理员创建的用户首次必须改密
    )
    if req.role_ids:
        role_result = await db.execute(select(Role).where(Role.id.in_(req.role_ids)))
        user.roles = role_result.scalars().all()
    db.add(user)
    await db.flush()

    return ResponseModel(data={"id": user.id, "username": user.username}, message="用户创建成功")


@router.put("/users/{user_id}", summary="编辑账号", description="修改员工姓名、部门、工号等基本信息", dependencies=[Depends(require_admin())])
async def update_user(
    user_id: int,
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(
            User.id == user_id, User.company_id == current_user.company_id, User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    for field in ["full_name", "email", "phone", "department", "employee_no"]:
        val = getattr(req, field, None)
        if val is not None:
            setattr(user, field, val)

    if req.role_ids is not None:
        role_result = await db.execute(select(Role).where(Role.id.in_(req.role_ids)))
        user.roles = role_result.scalars().all()

    await db.flush()
    return ResponseModel(message="用户更新成功")


@router.put("/users/{user_id}/status", summary="启用/停用账号", description="停用后该账号无法登录", dependencies=[Depends(require_admin())])
async def toggle_user_status(
    user_id: int,
    req: UserStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == current_user.company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.status = req.status
    await db.flush()
    return ResponseModel(message=f"用户已{'启用' if req.status == UserStatus.ACTIVE else '禁用'}")


@router.put("/users/{user_id}/reset-password", summary="重置密码", description="将密码重置为新密码，用户下次登录时需修改", dependencies=[Depends(require_admin())])
async def reset_password(
    user_id: int,
    req: ResetPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == current_user.company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.hashed_password = hash_password(req.new_password)
    user.must_change_password = True
    await db.flush()
    return ResponseModel(message="密码已重置，用户下次登录需修改密码")


# ═══════════════════ 角色管理 ═══════════════════

@router.get("/roles", dependencies=[Depends(require_admin())])
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Role).options(selectinload(Role.menus)).where(
            Role.company_id == current_user.company_id, Role.is_deleted == False
        )
    )
    roles = result.scalars().all()
    items = []
    for r in roles:
        items.append({
            "id": r.id, "name": r.name, "code": r.code, "description": r.description,
            "menus": [{"id": m.id, "name": m.name, "code": m.code} for m in r.menus],
        })
    return ResponseModel(data=items)


@router.post("/roles", dependencies=[Depends(require_admin())])
async def create_role(
    req: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = Role(
        company_id=current_user.company_id,
        name=req.name, code=req.code, description=req.description,
    )
    if req.menu_ids:
        menu_result = await db.execute(select(Menu).where(Menu.id.in_(req.menu_ids)))
        role.menus = menu_result.scalars().all()
    db.add(role)
    await db.flush()
    return ResponseModel(data={"id": role.id, "name": role.name}, message="角色创建成功")


# ═══════════════════ 菜单管理 ═══════════════════

@router.get("/menus", dependencies=[Depends(require_admin())])
async def list_menus(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Menu).where(Menu.is_deleted == False).order_by(Menu.sort_order)
    )
    menus = result.scalars().all()
    return ResponseModel(data=[{
        "id": m.id, "parent_id": m.parent_id, "name": m.name, "code": m.code,
        "type": m.type, "path": m.path, "icon": m.icon, "sort_order": m.sort_order,
    } for m in menus])


@router.get("/menus/tree")
async def get_menu_tree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """根据当前用户角色返回菜单树"""
    result = await db.execute(
        select(User).options(selectinload(User.roles).selectinload(Role.menus))
        .where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()
    menu_set = {}
    for role in user.roles:
        for menu in role.menus:
            if menu.type == "menu":
                menu_set[menu.id] = menu

    menus = sorted(menu_set.values(), key=lambda m: m.sort_order)

    # 构建树
    menu_map = {m.id: {
        "id": m.id, "name": m.name, "code": m.code,
        "path": m.path, "icon": m.icon, "children": []
    } for m in menus}

    tree = []
    for m in menus:
        node = menu_map[m.id]
        if m.parent_id and m.parent_id in menu_map:
            menu_map[m.parent_id]["children"].append(node)
        else:
            tree.append(node)
    return ResponseModel(data=tree)
