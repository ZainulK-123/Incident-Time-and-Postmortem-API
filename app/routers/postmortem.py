from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.postmortem import PostmortemCreate, PostmortemResponse, PostmortemUpdate, PostmortemInDB
from app.models.user import UserInDB
from app.database import get_database
from app.routers.auth import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/postmortems", tags=["Postmortems"])

@router.post("/", response_model=PostmortemResponse)
async def create_postmortem(postmortem: PostmortemCreate, current_user: UserInDB = Depends(get_current_user), db=Depends(get_database)):
    if not ObjectId.is_valid(postmortem.incident_id):
        raise HTTPException(status_code=400, detail="Invalid Incident ID format")
        
    incident = await db.incidents.find_one({"_id": ObjectId(postmortem.incident_id)})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    existing_postmortem = await db.postmortems.find_one({"incident_id": postmortem.incident_id})
    if existing_postmortem:
        raise HTTPException(status_code=400, detail="Postmortem already exists for this incident")

    postmortem_in_db = PostmortemInDB(
        **postmortem.dict()
    )
    new_postmortem = await db.postmortems.insert_one(postmortem_in_db.dict(by_alias=True, exclude={"id"}))
    created_postmortem = await db.postmortems.find_one({"_id": new_postmortem.inserted_id})
    return PostmortemResponse(**created_postmortem)

@router.get("/incident/{incident_id}", response_model=PostmortemResponse)
async def get_incident_postmortem(incident_id: str, db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(incident_id):
        raise HTTPException(status_code=400, detail="Invalid Incident ID format")
        
    postmortem = await db.postmortems.find_one({"incident_id": incident_id})
    if postmortem is None:
        raise HTTPException(status_code=404, detail="Postmortem not found")
    return PostmortemResponse(**postmortem)

@router.put("/{postmortem_id}", response_model=PostmortemResponse)
async def update_postmortem(postmortem_id: str, postmortem_update: PostmortemUpdate, db=Depends(get_database), current_user: UserInDB = Depends(get_current_user)):
    if not ObjectId.is_valid(postmortem_id):
        raise HTTPException(status_code=400, detail="Invalid Postmortem ID format")
        
    update_data = {k: v for k, v in postmortem_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    if len(update_data) >= 1:
        update_result = await db.postmortems.update_one({"_id": ObjectId(postmortem_id)}, {"$set": update_data})
        if update_result.modified_count == 1:
            updated_postmortem = await db.postmortems.find_one({"_id": ObjectId(postmortem_id)})
            return PostmortemResponse(**updated_postmortem)
            
    existing_postmortem = await db.postmortems.find_one({"_id": ObjectId(postmortem_id)})
    if existing_postmortem is None:
         raise HTTPException(status_code=404, detail="Postmortem not found")
         
    return PostmortemResponse(**existing_postmortem)
