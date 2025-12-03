from fastapi import APIRouter, HTTPException
from config import timeline_collection, incidents_collection
from database.schemas import timeline_event_serializer, timeline_events_serializer
from database.models import TimelineEvent
from bson.objectid import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/", status_code=201)
async def add_timeline_event(event: TimelineEvent):
    """Add a timeline event to an incident"""
    try:
        # Verify incident exists
        if not ObjectId.is_valid(event.incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        incident = incidents_collection.find_one({"_id": ObjectId(event.incident_id)})
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        event_dict = event.dict()
        event_dict["timestamp"] = datetime.now()
        
        result = timeline_collection.insert_one(event_dict)
        created_event = timeline_collection.find_one({"_id": result.inserted_id})
        
        return {
            "status_code": 201,
            "message": "Timeline event added successfully",
            "data": timeline_event_serializer(created_event)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding timeline event: {str(e)}")

@router.get("/{incident_id}")
async def get_timeline(incident_id: str):
    """Fetch all timeline events for an incident (sorted chronologically)"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        # Verify incident exists
        incident = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Fetch timeline events sorted by timestamp
        events = timeline_collection.find({"incident_id": incident_id}).sort("timestamp", 1)
        events_list = list(events)
        
        return {
            "status_code": 200,
            "incident_id": incident_id,
            "count": len(events_list),
            "data": timeline_events_serializer(events_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching timeline: {str(e)}")

@router.put("/{event_id}")
async def update_timeline_event(event_id: str, updated_event: TimelineEvent):
    """Update a timeline event"""
    try:
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID format")
        
        existing_event = timeline_collection.find_one({"_id": ObjectId(event_id)})
        if not existing_event:
            raise HTTPException(status_code=404, detail="Timeline event not found")
        
        update_dict = updated_event.dict(exclude_unset=True)
        
        timeline_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_dict}
        )
        
        updated = timeline_collection.find_one({"_id": ObjectId(event_id)})
        return {
            "status_code": 200,
            "message": "Timeline event updated successfully",
            "data": timeline_event_serializer(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating timeline event: {str(e)}")

@router.delete("/{event_id}")
async def delete_timeline_event(event_id: str):
    """Delete a timeline event"""
    try:
        if not ObjectId.is_valid(event_id):
            raise HTTPException(status_code=400, detail="Invalid event ID format")
        
        result = timeline_collection.delete_one({"_id": ObjectId(event_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Timeline event not found")
        
        return {
            "status_code": 200,
            "message": "Timeline event deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting timeline event: {str(e)}")
