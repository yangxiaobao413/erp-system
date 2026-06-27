from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import User, Company, Role, UserStatus, Menu
from app.schemas import (
    LoginRequest, ChangePasswordRequest, RefreshTokenRequest,
    UserCreateRequest, TokenResponse, ResponseModel,
)
from app.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["账户"])


@router.post("/register", include_in_schema=False)
async def register(body: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    company = Company(name=body.full_name or body.username)
    db.add(company)
    await db.flush()

    admin_role = Role(name="超级管理员", code="admin", company_id=company.id)
    db.add(admin_role)
    await db.flush()

    user = User(
        company_id=company.id,
        username=body.username,
        employee_no=body.employee_no or "",
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        email=body.email,
        department=body.department,
        must_change_password=False,
    )
    user.roles.append(admin_role)
    db.add(user)
    await db.flush()

    access_token = create_access_token({"sub": str(user.id), "company_id": user.company_id})
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token
    await db.flush()

    return ResponseModel(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "must_change_password": False,
        "user": {
            "id": user.id, "username": user.username,
            "full_name": user.full_name, "company_id": user.company_id,
            "company_name": company.name,
        },
    }, message="注册成功")


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).options(selectinload(User.company))
        .where(User.username == req.username, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if user.status == UserStatus.DISABLED:
        raise HTTPException(status_code=401, detail="账户已被禁用")

    access_token = create_access_token({"sub": str(user.id), "company_id": user.company_id})
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token
    await db.flush()

    return ResponseModel(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "must_change_password": user.must_change_password,
        "user": {
            "id": user.id, "username": user.username,
            "full_name": user.full_name, "employee_no": user.employee_no,
            "department": user.department, "company_id": user.company_id,
            "company_name": user.company.name,
        },
    }, message="登录成功")


@router.post("/refresh", include_in_schema=False)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="刷新令牌无效或已过期")

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user or user.refresh_token != req.refresh_token:
        raise HTTPException(status_code=401, detail="刷新令牌不匹配")

    new_access = create_access_token({"sub": str(user.id), "company_id": user.company_id})
    new_refresh = create_refresh_token(user.id)
    user.refresh_token = new_refresh
    await db.flush()

    return ResponseModel(data={
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }, message="令牌刷新成功")


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.hashed_password = hash_password(req.new_password)
    current_user.must_change_password = False
    await db.flush()
    return ResponseModel(message="密码修改成功")


@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).options(
            selectinload(User.company),
            selectinload(User.roles).selectinload(Role.menus)
        ).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    roles_data = []
    permissions = []
    for role in user.roles:
        roles_data.append({"id": role.id, "name": role.name, "code": role.code})
        for menu in role.menus:
            permissions.append(menu.code)

    return ResponseModel(data={
        "id": user.id,
        "username": user.username,
        "employee_no": user.employee_no,
        "full_name": user.full_name,
        "email": user.email,
        "department": user.department,
        "company_id": user.company_id,
        "company_name": user.company.name if user.company else "",
        "roles": roles_data,
        "permissions": permissions,
        "must_change_password": user.must_change_password,
    })
