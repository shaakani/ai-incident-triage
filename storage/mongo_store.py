"""
MongoDB storage module for incident reports.
Replaces flat JSON file storage with a proper database.
"""
from datetime import datetime
from pymongo import MongoClient
from pymongo.collection import Collection


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "triage_db"
COLLECTION_NAME = "incidents"


def get_collection() -> Collection:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


def save_incident(action: str, result: dict, triage: dict) -> str:
    """Save an incident report to MongoDB."""
    collection = get_collection()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    incident_id = f"INC-{ts}"

    document = {
        "incident_id": incident_id,
        "created_at": datetime.now().isoformat(),
        "severity": triage.get("severity"),
        "category": triage.get("category"),
        "title": triage.get("title"),
        "sox_risk": triage.get("sox_risk"),
        "affected_services": triage.get("affected_services"),
        "action_taken": action,
        "action_result": result,
        "triage": triage,
    }

    collection.insert_one(document)
    print(f"  [MongoDB] Incident saved: {incident_id}")
    return incident_id


def get_incidents(limit: int = 50, severity: str = None, sox_risk: bool = None) -> list:
    """Query incidents from MongoDB with optional filters."""
    collection = get_collection()
    query = {}
    if severity:
        query["severity"] = severity
    if sox_risk is not None:
        query["sox_risk"] = sox_risk

    incidents = list(
        collection.find(query, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )
    return incidents


def get_incident_stats() -> dict:
    """Get summary statistics for the dashboard."""
    collection = get_collection()
    total = collection.count_documents({})
    p1_count = collection.count_documents({"severity": "P1"})
    p2_count = collection.count_documents({"severity": "P2"})
    sox_count = collection.count_documents({"sox_risk": True})

    return {
        "total": total,
        "p1": p1_count,
        "p2": p2_count,
        "sox_risk": sox_count,
    }