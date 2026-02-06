from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import get_db
from app.security import hash_password
from app.routes import auth_router, users_router, analytics_router, detect_router
from app.socket_server import create_socket_app


fastapi_app = FastAPI(title="PPE Detection Admin API")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(auth_router)
fastapi_app.include_router(users_router)
fastapi_app.include_router(analytics_router)
fastapi_app.include_router(detect_router)

@fastapi_app.on_event("startup")
async def ensure_admin_user():
    db = get_db()
    try:
        await db.command("ping")
    except Exception as exc:
        print(
            "MongoDB connection failed. Check MONGO_URL and that MongoDB is running."
        )
        raise exc
    if len(settings.admin_password.encode("utf-8")) > 72:
        print("ADMIN_PASSWORD is longer than 72 bytes (bcrypt limit). Update .env and restart.")
        return
    existing = await db.users.find_one({"username": settings.admin_username})
    if not existing:
        await db.users.insert_one(
            {
                "username": settings.admin_username,
                "password_hash": hash_password(settings.admin_password),
                "role": "admin",
                "is_active": True,
            }
        )

app = create_socket_app(fastapi_app)
