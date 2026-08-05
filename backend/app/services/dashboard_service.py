from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.product import Product
from app.models.device import Device
from app.models.activation_request import ActivationRequest, ActivationRequestStatus
from app.models.license import License
from app.common.enums import LicenseStatus
from app.models.audit import AuditLog
from app.schemas.dashboard import DashboardStatsResponse, DashboardOverview, RecentActivityEvent, SystemHealth

class DashboardService:
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> DashboardStatsResponse:
        # Overview stats
        orgs_count = await db.scalar(select(func.count(Organization.id))) or 0
        products_count = await db.scalar(select(func.count(Product.id))) or 0
        devices_count = await db.scalar(select(func.count(Device.id))) or 0
        
        # Online devices (seen in the last 15 minutes)
        fifteen_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=15)
        online_devices_count = await db.scalar(select(func.count(Device.id)).where(Device.last_seen >= fifteen_mins_ago)) or 0
        
        pending_requests_count = await db.scalar(
            select(func.count(ActivationRequest.id))
            .where(ActivationRequest.status == ActivationRequestStatus.PENDING.value)
        ) or 0
        
        active_licenses_count = await db.scalar(
            select(func.count(License.id))
            .where(License.status == LicenseStatus.ACTIVE)
        ) or 0
        
        expired_licenses_count = await db.scalar(
            select(func.count(License.id))
            .where(License.status == LicenseStatus.EXPIRED)
        ) or 0

        # Recent Activity
        recent_logs = await db.scalars(
            select(AuditLog)
            .order_by(AuditLog.timestamp.desc())
            .limit(10)
        )
        recent_activity = []
        for log in recent_logs.all():
            # Format message intelligently based on entity and action
            message = DashboardService._format_audit_message(log)
            recent_activity.append(
                RecentActivityEvent(
                    id=log.id,
                    timestamp=log.timestamp.isoformat(),
                    message=message
                )
            )

        # System Health (Basic placeholder logic for now, all green if DB query succeeded)
        system_health = SystemHealth(
            backend="healthy",
            database="healthy",
            storage="healthy",
            licensing_service="healthy"
        )

        overview = DashboardOverview(
            organizations=orgs_count,
            products=products_count,
            devices=devices_count,
            online_devices=online_devices_count,
            pending_requests=pending_requests_count,
            active_licenses=active_licenses_count,
            expired_licenses=expired_licenses_count
        )

        return DashboardStatsResponse(
            overview=overview,
            recent_activity=recent_activity,
            system_health=system_health
        )

    @staticmethod
    def _format_audit_message(log: AuditLog) -> str:
        # Example format: "prika@kai.com created a new Organization"
        actor = log.actor or "System"
        
        # Shorten actor to just username/email prefix if it's an email
        if "@" in actor:
            actor = actor.split("@")[0]
            actor = actor.capitalize()

        action = log.action.lower()
        entity = log.entity.replace("_", " ").title()

        if action == "create":
            return f"{actor} created a new {entity}"
        elif action == "update":
            return f"{actor} updated {entity}"
        elif action == "delete":
            return f"{actor} deleted {entity}"
        elif action == "generate":
            return f"{actor} generated a {entity}"
        elif action == "upload":
            return f"{actor} uploaded {entity}"
        elif action == "login":
            return f"{actor} logged in"
        elif action == "activate":
            return f"{actor} activated {entity}"
        else:
            return f"{actor} performed {action} on {entity}"

dashboard_service = DashboardService()
