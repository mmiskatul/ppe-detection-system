import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import FileResponse

from app.detect import detect_image, detect_video
from app.db import get_db
from app.deps import require_admin
from app.services.analytics import save_prevention_record_from_detection
from app.socket_server import emit_event


router = APIRouter(prefix="/detect", tags=["detect"])


@router.post("/image", dependencies=[Depends(require_admin)])
async def detect_image_endpoint(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    annotated_image, detections, counts, output_path = detect_image(
        tmp_path, original_filename=os.path.splitext(file.filename)[0]
    )
    db = get_db()
    summary = await save_prevention_record_from_detection(db, counts)
    await emit_event("prevention_saved", summary)
    await emit_event("analytics_updated", summary)
    return {"output_path": output_path, "detections": detections, "summary": counts, "analytics": summary}


@router.post("/video", dependencies=[Depends(require_admin)])
async def detect_video_endpoint(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    output_path, counts = detect_video(tmp_path)
    db = get_db()
    summary = await save_prevention_record_from_detection(db, counts)
    await emit_event("prevention_saved", summary)
    await emit_event("analytics_updated", summary)
    return {"output_path": output_path, "summary": counts, "analytics": summary}


@router.get("/download", dependencies=[Depends(require_admin)])
async def download_file(path: str):
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
