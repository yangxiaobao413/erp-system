from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.config import get_settings
from app.database import engine, Base, AsyncSessionLocal
from app.models import Menu
from app.routers import auth, customers, products, orders, dashboard, admin

settings = get_settings()


async def init_default_menus():
    async with AsyncSessionLocal() as db:
        existing = (await db.execute(select(Menu).limit(1))).scalar_one_or_none()
        if existing:
            return
        system_menu = Menu(name="系统管理", code="system", type="menu", path="/system", icon="SettingOutlined", sort_order=90)
        dashboard_menu = Menu(code="dashboard:view", name="工作台", type="menu", path="/dashboard", icon="DashboardOutlined", sort_order=10)
        customer_menu = Menu(code="customer:list", name="客户管理", type="menu", path="/customer", icon="TeamOutlined", sort_order=20)
        product_menu = Menu(code="product:list", name="产品管理", type="menu", path="/product", icon="ShoppingOutlined", sort_order=30)
        order_menu = Menu(code="order:list", name="订单管理", type="menu", path="/order", icon="FileTextOutlined", sort_order=40)
        db.add_all([system_menu, dashboard_menu, customer_menu, product_menu, order_menu])
        await db.flush()
        db.add_all([
            Menu(name="用户管理", code="system:user", type="menu", path="/system/users", icon="UserOutlined", sort_order=91, parent_id=system_menu.id),
            Menu(name="角色管理", code="system:role", type="menu", path="/system/roles", icon="TeamOutlined", sort_order=92, parent_id=system_menu.id),
            Menu(code="customer:create", name="新增客户", type="button", sort_order=21, parent_id=customer_menu.id),
            Menu(code="customer:edit", name="编辑客户", type="button", sort_order=22, parent_id=customer_menu.id),
            Menu(code="customer:delete", name="删除客户", type="button", sort_order=23, parent_id=customer_menu.id),
            Menu(code="product:create", name="新增产品", type="button", sort_order=31, parent_id=product_menu.id),
            Menu(code="product:edit", name="编辑产品", type="button", sort_order=32, parent_id=product_menu.id),
            Menu(code="product:delete", name="删除产品", type="button", sort_order=33, parent_id=product_menu.id),
            Menu(code="order:create", name="创建订单", type="menu", path="/order/create", sort_order=41, parent_id=order_menu.id),
            Menu(code="order:status", name="订单状态变更", type="button", sort_order=42, parent_id=order_menu.id),
        ])
        await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_default_menus()
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(dashboard.router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    base_html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - API 文档",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters={"persistAuthorization": True, "defaultModelsExpandDepth": -1},
    )
    body = base_html.body.decode("utf-8")
    inject = '\n<script src="/static/swagger-cn.js"></script>\n</body>'
    body = body.replace("</body>", inject)
    return HTMLResponse(body)


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} API v{settings.APP_VERSION}"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}
