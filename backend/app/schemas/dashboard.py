from typing import List
from pydantic import BaseModel

class DashboardOverview(BaseModel):
    organizations: int
    products: int
    devices: int
    online_devices: int
    pending_requests: int
    active_licenses: int
    expired_licenses: int

class RecentActivityEvent(BaseModel):
    id: str
    timestamp: str
    message: str

class SystemHealth(BaseModel):
    backend: str
    database: str
    storage: str
    licensing_service: str

class DashboardStatsResponse(BaseModel):
    overview: DashboardOverview
    recent_activity: List[RecentActivityEvent]
    system_health: SystemHealth
