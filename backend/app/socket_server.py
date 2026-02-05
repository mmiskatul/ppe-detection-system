import socketio
from fastapi import FastAPI
from app.realtime import process_realtime_frame
import uvicorn

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
app = FastAPI()
socket_app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)

@sio.event
async def frame(sid, data):
    try:
        encoded_frame, counts = process_realtime_frame(data)
        await sio.emit("result", {"frame": encoded_frame, "counts": counts}, to=sid)
    except Exception as e:
        print("Error processing frame:", e)

if __name__ == "__main__":
    uvicorn.run(socket_app, host="127.0.0.1", port=8001)
