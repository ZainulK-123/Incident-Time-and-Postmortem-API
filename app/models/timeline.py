from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.user import PyObjectId
from bson import ObjectId

class TimelineEventType(str, Enum):
    STATUS_CHANGE = "Status Change"
    COMMENT = "Comment"
    ALERT = "Alert"
    ACTION = "Action"

class TimelineEventBase(BaseModel):
    incident_id: str
    description: str
    event_type: TimelineEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TimelineEventCreate(TimelineEventBase):
    pass

class TimelineEventUpdate(BaseModel):
    description: Optional[str] = None
    event_type: Optional[TimelineEventType] = None
    timestamp: Optional[datetime] = None

class TimelineEventInDB(TimelineEventBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    author_id: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class TimelineEventResponse(TimelineEventInDB):
    pass
