from fastapi import APIRouter, HTTPException, Query
from config import incidents_collection
from database.schemas import incident_serializer, incidents_serializer
from database.models import Incident, IncidentStatus
from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("/", status_code=201)
async def create_incident(incident: Incident):
    """Create a new incident"""
    try:
        incident_dict = incident.dict()
        incident_dict["created_at"] = datetime.now()
        incident_dict["updated_at"] = datetime.now()
        
        result = incidents_collection.insert_one(incident_dict)
        created_incident = incidents_collection.find_one({"_id": result.inserted_id})
        
        return {
            "status_code": 201,
            "message": "Incident created successfully",
            "data": incident_serializer(created_incident)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating incident: {str(e)}")

@router.get("/")
async def get_all_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity")
):
    """Fetch all incidents with optional filters"""
    try:
        query = {}
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity
        
        incidents = incidents_collection.find(query)
        return {
            "status_code": 200,
            "count": incidents_collection.count_documents(query),
            "data": incidents_serializer(incidents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching incidents: {str(e)}")

@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    """Fetch a specific incident by ID"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        incident = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        return {
            "status_code": 200,
            "data": incident_serializer(incident)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching incident: {str(e)}")

@router.put("/{incident_id}")
async def update_incident(incident_id: str, updated_incident: Incident):
    """Update an existing incident"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        existing_incident = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        if not existing_incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        update_dict = updated_incident.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.now()
        
        # If status is changed to Resolved or Closed, set resolved_at
        if updated_incident.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            if not existing_incident.get("resolved_at"):
                update_dict["resolved_at"] = datetime.now()
        
        incidents_collection.update_one(
            {"_id": ObjectId(incident_id)},
            {"$set": update_dict}
        )
        
        updated = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        return {
            "status_code": 200,
            "message": "Incident updated successfully",
            "data": incident_serializer(updated)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating incident: {str(e)}")

@router.delete("/{incident_id}")
async def delete_incident(incident_id: str):
    """Delete an incident"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        result = incidents_collection.delete_one({"_id": ObjectId(incident_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        return {
            "status_code": 200,
            "message": "Incident deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting incident: {str(e)}")
