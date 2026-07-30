from enum import Enum

class BaseEnum(str, Enum):
    """Base class for all enums in the system."""
    
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
        
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
