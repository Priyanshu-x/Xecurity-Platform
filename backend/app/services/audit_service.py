import logging
from app.events.events import DomainEvent
from app.events.bus import event_bus
from app.models.audit import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

async def audit_listener(event: DomainEvent, db: AsyncSession = None, **kwargs):
    """
    Listens for DomainEvents and writes them to the AuditLog table.
    Requires a 'db' AsyncSession to be passed in the publish kwargs.
    """
    if db is None:
        logger.error("audit_listener requires a 'db' session keyword argument.")
        return
        
    audit_log = AuditLog(
        actor=event.actor,
        organization_id=event.organization_id,
        request_id=event.request_id,
        entity=event.entity,
        entity_id=event.entity_id,
        action=event.action,
        old_value=event.old_value,
        new_value=event.new_value,
        metadata_json=event.metadata,
        ip=event.ip,
        user_agent=event.user_agent,
        success=event.success,
        duration_ms=event.duration_ms
    )
    db.add(audit_log)
    # Important: Do not commit here if part of a transaction.
    # The caller will commit.

def setup_audit_logging():
    event_bus.subscribe(DomainEvent, audit_listener)
