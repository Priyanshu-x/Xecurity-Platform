from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.release import Release
from app.models.user import User
from app.schemas.release import ReleaseCreate, ReleaseUpdate
from app.repositories.release import release_repository
from app.repositories.product import product_repository
from app.events.bus import event_bus
from app.events.events import DomainEvent
from app.common.result import Result, Success, Failure, ConflictError, NotFoundError, ValidationError

class ReleaseService:
    @staticmethod
    async def create_release(db: AsyncSession, release_in: ReleaseCreate, current_user: User, request: Request) -> Result[Release]:
        # Validate product exists
        if not await product_repository.exists(db, id=release_in.product_id):
            return NotFoundError(message="Product not found.")

        # Prevent duplicate versions for same platform/architecture
        if await release_repository.exists(
            db, 
            product_id=release_in.product_id, 
            version=release_in.version, 
            platform=release_in.platform.value, 
            architecture=release_in.architecture.value
        ):
            return ConflictError(message="This version already exists for the specified platform and architecture.")

        # Prevent duplicate SHA256 across all releases (security constraint)
        if await release_repository.exists(db, sha256=release_in.sha256):
            return ConflictError(message="A release with this SHA256 hash already exists.")

        # Automatic demotion of previous `is_latest=True` if this one is marked as latest
        if release_in.is_latest:
            await release_repository.demote_latest_release(
                db, 
                product_id=release_in.product_id, 
                channel=release_in.channel.value, 
                platform=release_in.platform.value
            )

        # Set publishing metadata
        release_data = release_in.model_dump()
        release_data["published_at"] = datetime.now(timezone.utc)
        release_data["published_by"] = current_user.id
        
        # Ensure enums are string values for DB insertion, but pydantic should handle this.
        # Just in case, using model_dump handles it correctly if configured, but let's be explicit
        release_data["channel"] = release_in.channel.value
        release_data["platform"] = release_in.platform.value
        release_data["architecture"] = release_in.architecture.value
        release_data["installer_type"] = release_in.installer_type.value

        release = await release_repository.create(db, obj_in=ReleaseCreate(**release_data))
        
        await event_bus.publish(
            DomainEvent(
                actor=current_user.id,
                organization_id=current_user.organization_id,
                entity="Release",
                entity_id=release.id,
                action="CREATED_RELEASE",
                new_value={"version": release.version, "product_id": release.product_id, "channel": release.channel},
                ip=request.client.host if request and request.client else None
            ),
            db=db
        )
        return Success(release)

    @staticmethod
    async def list_releases(db: AsyncSession, product_id: str, include_deleted: bool = False) -> Result[List[Release]]:
        # Validate product exists
        if not await product_repository.exists(db, id=product_id):
            return NotFoundError(message="Product not found.")
            
        releases, _ = await release_repository.paginate(db, page=1, size=1000, include_deleted=include_deleted, product_id=product_id)
        return Success(releases)

    @staticmethod
    async def get_release(db: AsyncSession, release_id: str) -> Result[Release]:
        release = await release_repository.get(db, id=release_id)
        if not release or release.is_deleted:
            return NotFoundError(message="Release not found")
        return Success(release)

    @staticmethod
    async def update_release(db: AsyncSession, release_id: str, release_in: ReleaseUpdate, current_user: User, request: Request) -> Result[Release]:
        release = await release_repository.get(db, id=release_id)
        if not release or release.is_deleted:
            return NotFoundError(message="Release not found")
            
        update_data = release_in.model_dump(exclude_unset=True)
        
        # Check uniqueness if version/platform/arch changes
        if any(k in update_data for k in ["version", "platform", "architecture"]):
            version = update_data.get("version", release.version)
            platform = update_data.get("platform", release.platform)
            architecture = update_data.get("architecture", release.architecture)
            
            # Need to convert enums if present in update_data
            if hasattr(platform, "value"): platform = platform.value
            if hasattr(architecture, "value"): architecture = architecture.value
            
            # Check if this combination exists on another record
            existing = await db.execute(
                select(Release).where(
                    Release.product_id == release.product_id,
                    Release.version == version,
                    Release.platform == platform,
                    Release.architecture == architecture,
                    Release.id != release.id,
                    Release.is_deleted == False
                )
            )
            if existing.scalars().first():
                return ConflictError(message="This version already exists for the specified platform and architecture.")

        # If sha256 changed, ensure unique
        if "sha256" in update_data and update_data["sha256"] != release.sha256:
            if await release_repository.exists(db, sha256=update_data["sha256"]):
                return ConflictError(message="A release with this SHA256 hash already exists.")

        # Automatic demotion if marking as latest
        if update_data.get("is_latest") is True and not release.is_latest:
            channel = update_data.get("channel", release.channel)
            platform = update_data.get("platform", release.platform)
            if hasattr(channel, "value"): channel = channel.value
            if hasattr(platform, "value"): platform = platform.value
            
            await release_repository.demote_latest_release(
                db, 
                product_id=release.product_id, 
                channel=channel, 
                platform=platform
            )
            
        # Convert enums for DB update
        for field in ["channel", "platform", "architecture", "installer_type"]:
            if field in update_data and hasattr(update_data[field], "value"):
                update_data[field] = update_data[field].value

        release = await release_repository.update(db, db_obj=release, obj_in=update_data)
        
        await event_bus.publish(
            DomainEvent(
                actor=current_user.id,
                organization_id=current_user.organization_id,
                entity="Release",
                entity_id=release.id,
                action="UPDATED_RELEASE",
                new_value={"updated_fields": list(update_data.keys())},
                ip=request.client.host if request and request.client else None
            ),
            db=db
        )
        return Success(release)

    @staticmethod
    async def delete_release(db: AsyncSession, release_id: str, current_user: User, request: Request) -> Result[bool]:
        release = await release_repository.get(db, id=release_id)
        if not release or release.is_deleted:
            return NotFoundError(message="Release not found")
            
        await release_repository.soft_delete(db, id=release_id)
        
        await event_bus.publish(
            DomainEvent(
                actor=current_user.id,
                organization_id=current_user.organization_id,
                entity="Release",
                entity_id=release.id,
                action="DELETED_RELEASE",
                ip=request.client.host if request and request.client else None
            ),
            db=db
        )
        return Success(True)

release_service = ReleaseService()
