from datetime import datetime
from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "admin"
    is_active: bool = True


class UserPublic(BaseModel):
    id: str = Field(alias="_id")
    username: str
    role: str
    is_active: bool


class PreventionRecordCreate(BaseModel):
    user_id: str
    ppe_missing: list[str]
    violation_type: str
    estimated_savings: float


class IncidentRecordCreate(BaseModel):
    user_id: str
    description: str


class AnalyticsSummary(BaseModel):
    ppe_compliance_percent: float
    total_incidents: int
    weekly_summaries: list[dict]
    top_violation_types: list[dict]
    high_risk_days: list[dict]
    estimated_savings: float
