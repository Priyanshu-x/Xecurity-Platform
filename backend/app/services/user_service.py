from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User, UserRole
from app.core.security import get_password_hash

class UserService:
    async def get_all(self, db: AsyncSession) -> List[User]:
        # Exclude passwords in responses, but the schema handles that.
        return await user_repository.get_multi(db)

    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[User]:
        return await user_repository.get(db, id)

    async def create(self, db: AsyncSession, user_in: UserCreate) -> User:
        # Check duplicate email
        existing_user = await user_repository.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        create_data = user_in.model_dump(exclude={"password"})
        create_data["hashed_password"] = get_password_hash(user_in.password)
        
        return await user_repository.create(db, obj_in=create_data)

    async def update(self, db: AsyncSession, id: str, user_in: UserUpdate, current_user_id: str) -> User:
        user = await user_repository.get(db, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Check self-disable/downgrade protection
        if user.id == current_user_id:
            if user_in.is_active is False:
                raise HTTPException(status_code=400, detail="Cannot disable your own account.")
            if user_in.role is not None and user.role == UserRole.OWNER and user_in.role != UserRole.OWNER:
                raise HTTPException(status_code=400, detail="Cannot downgrade your own OWNER role.")

        # Last Owner protection
        if user.role == UserRole.OWNER:
            if (user_in.is_active is False) or (user_in.role is not None and user_in.role != UserRole.OWNER):
                owner_count = await user_repository.count_owners(db)
                if owner_count <= 1:
                    raise HTTPException(status_code=400, detail="Cannot disable or downgrade the last OWNER.")

        update_data = user_in.model_dump(exclude_unset=True, exclude={"password"})
        if user_in.password:
            update_data["hashed_password"] = get_password_hash(user_in.password)

        return await user_repository.update(db, db_obj=user, obj_in=update_data)

    async def disable(self, db: AsyncSession, id: str, current_user_id: str) -> User:
        # Alias for setting is_active = False
        update_schema = UserUpdate(is_active=False)
        return await self.update(db, id, update_schema, current_user_id)

user_service = UserService()
