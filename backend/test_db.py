import asyncio
from app.database import engine, async_session
from app.models import User
from sqlalchemy import select

async def test():
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "yangxiaobao"))
        u = result.scalar_one_or_none()
        if u:
            print(f"Found: {u.username}, company_id: {u.company_id}")
        else:
            print("User NOT found")
    await engine.dispose()

asyncio.run(test())
