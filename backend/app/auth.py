import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config import get_settings
from app.database import get_db
from app.models import User, Role, Menu, UserStatus

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ── Access Token ──
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ── Refresh Token ──
def create_refresh_token(user_id: int) -> str:
    token = uuid.uuid4().hex + uuid.uuid4().hex
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh", "jti": token}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ── 获取当前用户 ──
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="无效的访问令牌")
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    result = await db.execute(
        select(User).options(selectinload(User.roles).selectinload(Role.menus))
        .where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user or user.status == UserStatus.DISABLED:
        raise HTTPException(status_code=401, detail="账户已被禁用或不存在")
    return user


# ── 权限检查 ──
class PermissionChecker:
    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    async def __call__(self, current_user: User = Depends(get_current_user)):
        user_permissions = set()
        for role in current_user.roles:
            for menu in role.menus:
                user_permissions.add(menu.code)
        # admin 角色拥有所有权限
        if "admin" in [r.code for r in current_user.roles]:
            return current_user
        for perm in self.required_permissions:
            if perm not in user_permissions:
                raise HTTPException(status_code=403, detail=f"权限不足，需要: {perm}")
        return current_user


# 便捷函数
def require_admin():
    return PermissionChecker(["admin"])


def require_permission(*perms: str):
    return PermissionChecker(list(perms))
