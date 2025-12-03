from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums for validation
class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class IncidentStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class EventType(str, Enum):
    DETECTION = "Detection"
    INVESTIGATION = "Investigation"
    MITIGATION = "Mitigation"
    RESOLUTION = "Resolution"

# Incident Model
class Incident(BaseModel):
    title: str
    description: str
    severity: SeverityLevel = SeverityLevel.MEDIUM
    status: IncidentStatus = IncidentStatus.OPEN
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        use_enum_values = True

# Timeline Event Model
class TimelineEvent(BaseModel):
    incident_id: str
    event_type: EventType
    description: str
    timestamp: Optional[datetime] = None
    created_by: str = "system"

    class Config:
        use_enum_values = True

# Postmortem Model
class Postmortem(BaseModel):
    incident_id: str
    root_cause: str = ""
    contributing_factors: List[str] = []
    impact: str = ""
    action_items: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
