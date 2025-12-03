# Incident Schemas
def incident_serializer(incident) -> dict:
    return {
        "id": str(incident["_id"]),
        "title": incident["title"],
        "description": incident["description"],
        "severity": incident["severity"],
        "status": incident["status"],
        "created_at": incident.get("created_at"),
        "updated_at": incident.get("updated_at"),
        "resolved_at": incident.get("resolved_at")
    }

def incidents_serializer(incidents) -> list:
    return [incident_serializer(incident) for incident in incidents]

# Timeline Event Schemas
def timeline_event_serializer(event) -> dict:
    return {
        "id": str(event["_id"]),
        "incident_id": event["incident_id"],
        "event_type": event["event_type"],
        "description": event["description"],
        "timestamp": event.get("timestamp"),
        "created_by": event.get("created_by", "system")
    }

def timeline_events_serializer(events) -> list:
    return [timeline_event_serializer(event) for event in events]

# Postmortem Schemas
def postmortem_serializer(postmortem) -> dict:
    return {
        "id": str(postmortem["_id"]),
        "incident_id": postmortem["incident_id"],
        "root_cause": postmortem.get("root_cause", ""),
        "contributing_factors": postmortem.get("contributing_factors", []),
        "impact": postmortem.get("impact", ""),
        "action_items": postmortem.get("action_items", []),
        "created_at": postmortem.get("created_at"),
        "updated_at": postmortem.get("updated_at")
    }
