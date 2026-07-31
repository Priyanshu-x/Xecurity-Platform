from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from sqlalchemy.future import select

from app.models.release import Release, ReleaseArtifact, ReleaseStatus
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
        if not await product_repository.exists(db, id=release_in.product_id):
            return NotFoundError(message="Product not found.")

        # Check unique version+build_number
        if await release_repository.exists(
            db, 
            product_id=release_in.product_id, 
            version=release_in.version, 
            build_number=release_in.build_number
        ):
            return ConflictError(message="This version and build number already exists.")

        # Automatic demotion if marking as latest
        if release_in.is_latest:
            await release_repository.demote_latest_release(
                db, 
                product_id=release_in.product_id, 
                channel=release_in.channel.value
            )

        release_data = release_in.model_dump(exclude={"artifacts"})
        
        # Enforce PUBLISHED status logic
        if release_data.get("status") == ReleaseStatus.PUBLISHED.value:
            release_data["published_at"] = datetime.now(timezone.utc)
            release_data["published_by"] = current_user.id
            
        release_data["channel"] = release_in.channel.value
        
        # Create Release
        release = await release_repository.create(db, obj_in=ReleaseCreate(**release_data))
        
        # Create Artifacts
        if release_in.artifacts:
            for artifact_in in release_in.artifacts:
                art_data = artifact_in.model_dump()
                art_data["release_id"] = release.id
                art_data["platform"] = artifact_in.platform.value
                art_data["architecture"] = artifact_in.architecture.value
                art_data["artifact_type"] = artifact_in.artifact_type.value
                
                db_artifact = ReleaseArtifact(**art_data)
                db.add(db_artifact)
            await db.flush()
            await db.refresh(release)
        
        await event_bus.publish(
            DomainEvent(
                actor=current_user.id,
                organization_id=current_user.organization_id,
                entity="Release",
                entity_id=release.id,
                action="CREATED_RELEASE",
                new_value={"version": release.version, "build_number": release.build_number, "channel": release.channel},
                ip=request.client.host if request and request.client else None
            ),
            db=db
        )
        return Success(release)

    @staticmethod
    async def list_releases(db: AsyncSession, product_id: Optional[str] = None, include_deleted: bool = False, **kwargs) -> Result[List[Release]]:
        filters = {}
        if product_id:
            if not await product_repository.exists(db, id=product_id):
                return NotFoundError(message="Product not found.")
            filters["product_id"] = product_id
            
        filters.update(kwargs)
        releases, _ = await release_repository.paginate(db, page=1, size=1000, include_deleted=include_deleted, **filters)
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
            
        # Immutability Check
        if release.status == ReleaseStatus.PUBLISHED.value or release.status == ReleaseStatus.ARCHIVED.value:
            # We allow deprecating or archiving a published release, but not editing its core fields.
            allowed_fields = {"status", "is_latest", "release_notes"}
            update_data = release_in.model_dump(exclude_unset=True)
            for k in update_data.keys():
                if k not in allowed_fields:
                    return ConflictError(message="Cannot modify a published or archived release. Create a new release instead.")
        else:
            update_data = release_in.model_dump(exclude_unset=True)

        if "version" in update_data or "build_number" in update_data:
            version = update_data.get("version", release.version)
            build_number = update_data.get("build_number", release.build_number)
            
            existing = await db.execute(
                select(Release).where(
                    Release.product_id == release.product_id,
                    Release.version == version,
                    Release.build_number == build_number,
                    Release.id != release.id,
                    Release.is_deleted == False
                )
            )
            if existing.scalars().first():
                return ConflictError(message="This version and build number already exists.")

        # Automatic demotion if marking as latest
        if update_data.get("is_latest") is True and not release.is_latest:
            channel = update_data.get("channel", release.channel)
            if hasattr(channel, "value"): channel = channel.value
            
            await release_repository.demote_latest_release(
                db, 
                product_id=release.product_id, 
                channel=channel
            )
            
        if "channel" in update_data and hasattr(update_data["channel"], "value"):
            update_data["channel"] = update_data["channel"].value
        if "status" in update_data and hasattr(update_data["status"], "value"):
            update_data["status"] = update_data["status"].value
            if update_data["status"] == ReleaseStatus.PUBLISHED.value and release.status != ReleaseStatus.PUBLISHED.value:
                update_data["published_at"] = datetime.now(timezone.utc)
                update_data["published_by"] = current_user.id

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

    @staticmethod
    async def check_update(db: AsyncSession, product_id: str, channel: str, current_build: int) -> Result[dict]:
        """Endpoint for client auto-update checks"""
        latest_release = await release_repository.get_latest_release(db, product_id, channel)
        if not latest_release or latest_release.status != ReleaseStatus.PUBLISHED.value:
            return Success({
                "update_available": False,
                "current_build": current_build,
                "latest_build": None,
                "release": None
            })
            
        update_available = latest_release.build_number > current_build
        
        return Success({
            "update_available": update_available,
            "mandatory": latest_release.mandatory if update_available else False,
            "reason": "New update available" if update_available else None,
            "current_build": current_build,
            "latest_build": latest_release.build_number,
            "release": latest_release if update_available else None
        })

release_service = ReleaseService()
