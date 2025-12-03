from fastapi import APIRouter, HTTPException
from config import postmortem_collection, incidents_collection, timeline_collection
from database.schemas import postmortem_serializer, incident_serializer, timeline_events_serializer
from database.models import Postmortem
from bson.objectid import ObjectId
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/{incident_id}/rca", status_code=201)
async def generate_rca(incident_id: str, root_cause: str):
    """Generate or update Root Cause Analysis for an incident"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        # Verify incident exists
        incident = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Check if postmortem already exists
        existing_postmortem = postmortem_collection.find_one({"incident_id": incident_id})
        
        if existing_postmortem:
            # Update existing postmortem
            postmortem_collection.update_one(
                {"incident_id": incident_id},
                {"$set": {
                    "root_cause": root_cause,
                    "updated_at": datetime.now()
                }}
            )
            updated = postmortem_collection.find_one({"incident_id": incident_id})
            return {
                "status_code": 200,
                "message": "RCA updated successfully",
                "data": postmortem_serializer(updated)
            }
        else:
            # Create new postmortem
            postmortem_dict = {
                "incident_id": incident_id,
                "root_cause": root_cause,
                "contributing_factors": [],
                "impact": "",
                "action_items": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            result = postmortem_collection.insert_one(postmortem_dict)
            created = postmortem_collection.find_one({"_id": result.inserted_id})
            return {
                "status_code": 201,
                "message": "RCA created successfully",
                "data": postmortem_serializer(created)
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating RCA: {str(e)}")

@router.post("/{incident_id}/factors")
async def add_contributing_factors(incident_id: str, factors: List[str]):
    """Add contributing factors to a postmortem"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        # Verify incident exists
        incident = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Check if postmortem exists
        existing_postmortem = postmortem_collection.find_one({"incident_id": incident_id})
        
        if not existing_postmortem:
            # Create new postmortem with factors
            postmortem_dict = {
                "incident_id": incident_id,
                "root_cause": "",
                "contributing_factors": factors,
                "impact": "",
                "action_items": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            result = postmortem_collection.insert_one(postmortem_dict)
            created = postmortem_collection.find_one({"_id": result.inserted_id})
            return {
                "status_code": 201,
                "message": "Contributing factors added successfully",
                "data": postmortem_serializer(created)
            }
        else:
            # Add to existing factors
            current_factors = existing_postmortem.get("contributing_factors", [])
            updated_factors = list(set(current_factors + factors))  # Remove duplicates
            
            postmortem_collection.update_one(
                {"incident_id": incident_id},
                {"$set": {
                    "contributing_factors": updated_factors,
                    "updated_at": datetime.now()
                }}
            )
            updated = postmortem_collection.find_one({"incident_id": incident_id})
            return {
                "status_code": 200,
                "message": "Contributing factors updated successfully",
                "data": postmortem_serializer(updated)
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding contributing factors: {str(e)}")

@router.get("/{incident_id}")
async def get_postmortem(incident_id: str):
    """Fetch postmortem report for an incident"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        # Verify incident exists
        incident = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        postmortem = postmortem_collection.find_one({"incident_id": incident_id})
        if not postmortem:
            raise HTTPException(status_code=404, detail="Postmortem not found for this incident")
        
        return {
            "status_code": 200,
            "data": postmortem_serializer(postmortem)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching postmortem: {str(e)}")

@router.post("/{incident_id}/generate")
async def generate_final_postmortem(incident_id: str, impact: str, action_items: List[str]):
    """Generate final comprehensive postmortem report"""
    try:
        if not ObjectId.is_valid(incident_id):
            raise HTTPException(status_code=400, detail="Invalid incident ID format")
        
        # Verify incident exists
        incident = incidents_collection.find_one({"_id": ObjectId(incident_id)})
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Get timeline events
        timeline_events = list(timeline_collection.find({"incident_id": incident_id}).sort("timestamp", 1))
        
        # Check if postmortem exists
        existing_postmortem = postmortem_collection.find_one({"incident_id": incident_id})
        
        if existing_postmortem:
            # Update with final details
            postmortem_collection.update_one(
                {"incident_id": incident_id},
                {"$set": {
                    "impact": impact,
                    "action_items": action_items,
                    "updated_at": datetime.now()
                }}
            )
            updated = postmortem_collection.find_one({"incident_id": incident_id})
            postmortem_data = postmortem_serializer(updated)
        else:
            # Create complete postmortem
            postmortem_dict = {
                "incident_id": incident_id,
                "root_cause": "",
                "contributing_factors": [],
                "impact": impact,
                "action_items": action_items,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            result = postmortem_collection.insert_one(postmortem_dict)
            created = postmortem_collection.find_one({"_id": result.inserted_id})
            postmortem_data = postmortem_serializer(created)
        
        # Return comprehensive report
        return {
            "status_code": 200,
            "message": "Final postmortem report generated successfully",
            "data": {
                "incident": incident_serializer(incident),
                "timeline": timeline_events_serializer(timeline_events),
                "postmortem": postmortem_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating final postmortem: {str(e)}")
