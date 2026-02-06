import asyncio
import random
from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URL = "mongodb://localhost:27017"
MONGO_DB = "ppe_detection"


PPE_CLASSES = ["Mask", "Helmet", "Vest", "Boots"]
VIOLATION_TYPES = ["missing_ppe", "unsafe_behavior", "equipment_fault"]


def _utc_now():
    return datetime.now(timezone.utc)


async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]

    await db.prevention_records.delete_many({})
    await db.incident_records.delete_many({})

    prevention_docs = []
    incident_docs = []
    base = _utc_now() - timedelta(days=30)

    for day in range(30):
        created_at = base + timedelta(days=day)
        for _ in range(random.randint(3, 8)):
            missing = random.sample(PPE_CLASSES, random.randint(0, 2))
            violation_type = "none" if not missing else random.choice(VIOLATION_TYPES)
            prevention_docs.append(
                {
                    "user_id": "system",
                    "ppe_missing": missing,
                    "violation_type": violation_type,
                    "estimated_savings": float(len(missing) * 250),
                    "created_at": created_at,
                }
            )
        if random.random() > 0.6:
            incident_docs.append(
                {
                    "user_id": "system",
                    "description": "Seeded incident",
                    "created_at": created_at,
                }
            )

    if prevention_docs:
        await db.prevention_records.insert_many(prevention_docs)
    if incident_docs:
        await db.incident_records.insert_many(incident_docs)

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
