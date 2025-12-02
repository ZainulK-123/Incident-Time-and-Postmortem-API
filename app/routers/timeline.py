from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.timeline import TimelineEventCreate, TimelineEventResponse, TimelineEventUpdate, TimelineEventInDB
from app.models.user import UserInDB
from app.database import get_database
from app.routers.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/timeline", tags=["Timeline"])

@router.post("/", response_model=TimelineEventResponse)
async def add_timeline_event(event: TimelineEventCreate, current_user: UserInDB = Depends(get_current_user), db=Depends(get_database)):
    if not ObjectId.is_valid(event.incident_id):
        raise HTTPException(status_code=400, detail="Invalid Incident ID format")
        
    incident = await db.incidents.find_one({"_id": ObjectId(event.incident_id)})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    event_in_db = TimelineEventInDB(
        **event.dict(),
        author_id=str(current_user.id)
    )
    new_event = await db.timeline.insert_one(event_in_db.dict(by_alias=True, exclude={"id"}))
    created_event = await db.timeline.find_one({"_id": new_event.inserted_id})
    return TimelineEventResponse(**created_event)

@router.get("/incident/{incident_id}", response_model=List[TimelineEventResponse])
async def get_incident_timeline(incident_id: str, db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(incident_id):
        raise HTTPException(status_code=400, detail="Invalid Incident ID format")
        
    events = await db.timeline.find({"incident_id": incident_id}).sort("timestamp", 1).to_list(1000)
    return [TimelineEventResponse(**event) for event in events]

@router.put("/{event_id}", response_model=TimelineEventResponse)
async def update_timeline_event(event_id: str, event_update: TimelineEventUpdate, db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid Event ID format")
        
    update_data = {k: v for k, v in event_update.dict().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await db.timeline.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})
        if update_result.modified_count == 1:
            updated_event = await db.timeline.find_one({"_id": ObjectId(event_id)})
            return TimelineEventResponse(**updated_event)
            
    existing_event = await db.timeline.find_one({"_id": ObjectId(event_id)})
    if existing_event is None:
         raise HTTPException(status_code=404, detail="Timeline event not found")
         
    return TimelineEventResponse(**existing_event)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline_event(event_id: str, db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=400, detail="Invalid Event ID format")
        
    delete_result = await db.timeline.delete_one({"_id": ObjectId(event_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    return
