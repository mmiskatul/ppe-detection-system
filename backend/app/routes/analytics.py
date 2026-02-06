from fastapi import APIRouter, Depends, status

from app.db import get_db
from app.deps import require_admin
from app.schemas import AnalyticsSummary, IncidentRecordCreate
from app.services.analytics import recalculate_analytics, save_incident_record
from app.socket_server import emit_event


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary, dependencies=[Depends(require_admin)])
async def get_summary():
    db = get_db()
    return await recalculate_analytics(db)


@router.post("/incidents", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_incident(payload: IncidentRecordCreate):
    db = get_db()
    summary = await save_incident_record(db, payload)
    await emit_event("incident_saved", summary)
    await emit_event("analytics_updated", summary)
    return summary
