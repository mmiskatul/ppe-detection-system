import pytest
from datetime import datetime, timezone, timedelta

from app.security import create_access_token


@pytest.mark.asyncio
async def test_analytics_summary(client, db):
    now = datetime.now(timezone.utc)
    await db.users.insert_one(
        {
            "username": "admin",
            "password_hash": "x",
            "role": "admin",
            "is_active": True,
        }
    )

    await db.prevention_records.insert_many(
        [
            {
                "user_id": "system",
                "ppe_missing": [],
                "violation_type": "none",
                "estimated_savings": 0.0,
                "created_at": now - timedelta(days=3),
            },
            {
                "user_id": "system",
                "ppe_missing": ["Helmet"],
                "violation_type": "missing_ppe",
                "estimated_savings": 250.0,
                "created_at": now - timedelta(days=2),
            },
        ]
    )
    await db.incident_records.insert_one(
        {"user_id": "system", "description": "test incident", "created_at": now}
    )

    token = create_access_token({"sub": "admin", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/analytics/summary", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_incidents"] == 1
    assert payload["ppe_compliance_percent"] == 50.0
    assert payload["estimated_savings"] == 250.0
    assert isinstance(payload["weekly_summaries"], list)
    assert isinstance(payload["top_violation_types"], list)
    assert isinstance(payload["high_risk_days"], list)
