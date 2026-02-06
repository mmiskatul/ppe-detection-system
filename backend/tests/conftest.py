import os
import pytest
import pytest_asyncio


os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("MONGO_DB", "ppe_detection_test")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db():
    from app.db import get_db

    database = get_db()
    await database.users.delete_many({})
    await database.prevention_records.delete_many({})
    await database.incident_records.delete_many({})
    yield database
    await database.users.delete_many({})
    await database.prevention_records.delete_many({})
    await database.incident_records.delete_many({})


@pytest_asyncio.fixture
async def client(db):
    from httpx import AsyncClient
    from app.main import fastapi_app

    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac
