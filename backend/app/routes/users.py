from fastapi import APIRouter, Depends, HTTPException, status

from app.db import get_db
from app.deps import require_admin
from app.schemas import UserCreate, UserPublic
from app.security import hash_password


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserPublic], dependencies=[Depends(require_admin)])
async def list_users():
    db = get_db()
    users = await db.users.find({}, {"password_hash": 0}).to_list(length=1000)
    for user in users:
        user["_id"] = str(user["_id"])
    return users


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_user(payload: UserCreate):
    db = get_db()
    existing = await db.users.find_one({"username": payload.username})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    doc = {
        "username": payload.username,
        "password_hash": hash_password(payload.password),
        "role": payload.role,
        "is_active": payload.is_active,
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc
