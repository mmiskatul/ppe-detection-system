from fastapi import APIRouter, HTTPException, status

from app.db import get_db
from app.schemas import LoginRequest, TokenResponse, UserPublic
from app.deps import get_current_user
from app.security import create_access_token, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    db = get_db()
    user = await db.users.find_one({"username": payload.username})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    role = user.get("role", "admin")
    token = create_access_token({"sub": user["username"], "role": role})
    return TokenResponse(access_token=token, role=role)


@router.get("/me", response_model=UserPublic)
async def me(current_user=Depends(get_current_user)):
    current_user["_id"] = str(current_user["_id"])
    return current_user
