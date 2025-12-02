from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.models.user import PyObjectId
from bson import ObjectId

class PostmortemStatus(str, Enum):
    DRAFT = "Draft"
    REVIEW = "Review"
    PUBLISHED = "Published"

class PostmortemBase(BaseModel):
    incident_id: str
    rca: Optional[str] = None
    contributing_factors: List[str] = []
    report_content: Optional[str] = None
    status: PostmortemStatus = PostmortemStatus.DRAFT

class PostmortemCreate(PostmortemBase):
    pass

class PostmortemUpdate(BaseModel):
    rca: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    report_content: Optional[str] = None
    status: Optional[PostmortemStatus] = None

class PostmortemInDB(PostmortemBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class PostmortemResponse(PostmortemInDB):
    pass
