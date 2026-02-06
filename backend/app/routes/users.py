from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

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


@router.patch("/{user_id}/activate", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def activate_user(user_id: str):
    db = get_db()
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True}},
        return_document=True,
        projection={"password_hash": 0},
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result["_id"] = str(result["_id"])
    return result


@router.patch("/{user_id}/deactivate", response_model=UserPublic, dependencies=[Depends(require_admin)])
async def deactivate_user(user_id: str):
    db = get_db()
    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}},
        return_document=True,
        projection={"password_hash": 0},
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    result["_id"] = str(result["_id"])
    return result
