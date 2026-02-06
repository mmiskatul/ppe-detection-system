import pytest

from app.security import hash_password


@pytest.mark.asyncio
async def test_login_and_user_lifecycle(client, db):
    await db.users.insert_one(
        {
            "username": "admin",
            "password_hash": hash_password("pass123"),
            "role": "admin",
            "is_active": True,
        }
    )

    login = await client.post("/auth/login", json={"username": "admin", "password": "pass123"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = await client.post(
        "/users",
        json={"username": "viewer1", "password": "viewerpass", "role": "viewer", "is_active": True},
        headers=headers,
    )
    assert created.status_code == 201
    user_id = created.json()["_id"]

    deactivated = await client.patch(f"/users/{user_id}/deactivate", headers=headers)
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    activated = await client.patch(f"/users/{user_id}/activate", headers=headers)
    assert activated.status_code == 200
    assert activated.json()["is_active"] is True

    listed = await client.get("/users", headers=headers)
    assert listed.status_code == 200
    assert any(user["username"] == "viewer1" for user in listed.json())
