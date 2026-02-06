from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas import IncidentRecordCreate


PPE_CLASSES = ["Mask", "Helmet", "Vest", "Boots"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _derive_prevention_payload(counts: dict[str, int]) -> dict[str, Any]:
    person_count = int(counts.get("Person", 0))
    missing = [ppe for ppe in PPE_CLASSES if int(counts.get(ppe, 0)) == 0 and person_count > 0]
    violation_type = "missing_ppe" if missing else "none"
    estimated_savings = float(len(missing) * 250.0)
    return {
        "user_id": "system",
        "ppe_missing": missing,
        "violation_type": violation_type,
        "estimated_savings": estimated_savings,
        "created_at": _utc_now(),
        "detection_total": int(sum(counts.values())),
    }


async def save_prevention_record_from_detection(
    db: AsyncIOMotorDatabase, counts: dict[str, int]
) -> dict[str, Any]:
    record = _derive_prevention_payload(counts)
    await db.prevention_records.insert_one(record)
    return await recalculate_analytics(db)


async def save_incident_record(
    db: AsyncIOMotorDatabase, payload: IncidentRecordCreate
) -> dict[str, Any]:
    doc = {
        "user_id": payload.user_id,
        "description": payload.description,
        "created_at": _utc_now(),
    }
    await db.incident_records.insert_one(doc)
    return await recalculate_analytics(db)


async def _weekly_summary(db: AsyncIOMotorDatabase) -> list[dict[str, Any]]:
    start = _utc_now() - timedelta(days=56)
    pipeline = [
        {"$match": {"created_at": {"$gte": start}}},
        {
            "$group": {
                "_id": {
                    "year": {"$isoWeekYear": "$created_at"},
                    "week": {"$isoWeek": "$created_at"},
                },
                "violations": {
                    "$sum": {
                        "$cond": [{"$eq": ["$violation_type", "none"]}, 0, 1]
                    }
                },
                "compliant": {
                    "$sum": {
                        "$cond": [{"$eq": ["$violation_type", "none"]}, 1, 0]
                    }
                },
            }
        },
        {"$sort": {"_id.year": 1, "_id.week": 1}},
    ]
    return await db.prevention_records.aggregate(pipeline).to_list(length=100)


async def _top_violation_types(db: AsyncIOMotorDatabase) -> list[dict[str, Any]]:
    pipeline = [
        {"$match": {"violation_type": {"$ne": "none"}}},
        {"$group": {"_id": "$violation_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
    ]
    return await db.prevention_records.aggregate(pipeline).to_list(length=10)


async def _high_risk_days(db: AsyncIOMotorDatabase) -> list[dict[str, Any]]:
    pipeline = [
        {
            "$project": {
                "day": {"$dayOfWeek": "$created_at"},
            }
        },
        {"$group": {"_id": "$day", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return await db.incident_records.aggregate(pipeline).to_list(length=10)


async def _compliance_percent(db: AsyncIOMotorDatabase) -> float:
    total = await db.prevention_records.count_documents({})
    if total == 0:
        return 100.0
    compliant = await db.prevention_records.count_documents({"violation_type": "none"})
    return round((compliant / total) * 100.0, 2)


async def _estimated_savings(db: AsyncIOMotorDatabase) -> float:
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$estimated_savings"}}}
    ]
    result = await db.prevention_records.aggregate(pipeline).to_list(length=1)
    return float(result[0]["total"]) if result else 0.0


async def recalculate_analytics(db: AsyncIOMotorDatabase) -> dict[str, Any]:
    ppe_compliance_percent = await _compliance_percent(db)
    total_incidents = await db.incident_records.count_documents({})
    weekly_summaries = await _weekly_summary(db)
    top_violation_types = await _top_violation_types(db)
    high_risk_days = await _high_risk_days(db)
    estimated_savings = await _estimated_savings(db)
    return {
        "ppe_compliance_percent": ppe_compliance_percent,
        "total_incidents": total_incidents,
        "weekly_summaries": weekly_summaries,
        "top_violation_types": top_violation_types,
        "high_risk_days": high_risk_days,
        "estimated_savings": estimated_savings,
    }
