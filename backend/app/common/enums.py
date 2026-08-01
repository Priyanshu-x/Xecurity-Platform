from enum import Enum

class BaseEnum(str, Enum):
    """Base class for all enums in the system."""
    
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
        
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class PlanTier(str, Enum):
    COMMUNITY = "COMMUNITY"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"
    GOVERNMENT = "GOVERNMENT"
    CUSTOM = "CUSTOM"

class PlanStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"

class SubscriptionStatus(BaseEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"
    TRIAL = "TRIAL"

class DeploymentEnvironment(BaseEnum):
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

class DeploymentStatus(BaseEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DECOMMISSIONED = "DECOMMISSIONED"

class LicenseStatus(BaseEnum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"
