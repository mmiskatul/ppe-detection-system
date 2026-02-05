from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from app.detect import detect_image, detect_video
import tempfile, shutil, os

app = FastAPI(title="PPE Detection API")

@app.post("/detect/image")
async def detect_image_endpoint(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        annotated_image, detections, counts, output_path = detect_image(tmp_path, original_filename=os.path.splitext(file.filename)[0])
        return {"output_path": output_path, "detections": detections, "summary": counts}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/detect/video")
async def detect_video_endpoint(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        output_path, counts = detect_video(tmp_path)
        return {"output_path": output_path, "summary": counts}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/download")
async def download_file(path: str):
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"error": "File not found"}, status_code=404)
