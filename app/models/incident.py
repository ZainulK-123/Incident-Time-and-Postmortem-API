from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.user import PyObjectId
from bson import ObjectId

class IncidentStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    MITIGATED = "Mitigated"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class IncidentSeverity(str, Enum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"

class IncidentBase(BaseModel):
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None

class IncidentInDB(IncidentBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class IncidentResponse(IncidentInDB):
    pass
