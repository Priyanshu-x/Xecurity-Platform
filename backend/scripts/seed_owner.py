import asyncio
import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

async def seed_owner():
    async with AsyncSessionLocal() as db:
        # Check if owner exists
        result = await db.execute(select(User).where(User.role == UserRole.OWNER))
        owner = result.scalar_one_or_none()
        if owner:
            print("Platform OWNER already exists.")
            return

        print("Creating Platform OWNER...")
        owner = User(
            email="admin@xecurity.com",
            hashed_password=get_password_hash("changeme123"),
            role=UserRole.OWNER,
            is_active=True,
        )
        db.add(owner)
        await db.commit()
        print("Platform OWNER created: admin@xecurity.com / changeme123")

if __name__ == "__main__":
    asyncio.run(seed_owner())
