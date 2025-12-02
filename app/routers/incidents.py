from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.incident import IncidentCreate, IncidentResponse, IncidentUpdate, IncidentInDB
from app.models.user import UserInDB
from app.database import get_database
from app.routers.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/", response_model=IncidentResponse)
async def create_incident(incident: IncidentCreate, current_user: UserInDB = Depends(get_current_user), db=Depends(get_database)):
    incident_in_db = IncidentInDB(
        **incident.dict(),
        created_by=current_user.username
    )
    new_incident = await db.incidents.insert_one(incident_in_db.dict(by_alias=True, exclude={"id"}))
    created_incident = await db.incidents.find_one({"_id": new_incident.inserted_id})
    return IncidentResponse(**created_incident)

@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    incidents = await db.incidents.find().to_list(1000)
    return [IncidentResponse(**incident) for incident in incidents]

@router.get("/{id}", response_model=IncidentResponse)
async def get_incident(id: str, db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    incident = await db.incidents.find_one({"_id": ObjectId(id)})
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse(**incident)

@router.put("/{id}", response_model=IncidentResponse)
async def update_incident(id: str, incident_update: IncidentUpdate, db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
        
    update_data = {k: v for k, v in incident_update.dict().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await db.incidents.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if update_result.modified_count == 1:
            updated_incident = await db.incidents.find_one({"_id": ObjectId(id)})
            return IncidentResponse(**updated_incident)
            
    existing_incident = await db.incidents.find_one({"_id": ObjectId(id)})
    if existing_incident is None:
         raise HTTPException(status_code=404, detail="Incident not found")
         
    return IncidentResponse(**existing_incident)
