import socketio
from fastapi import FastAPI
from jwt import PyJWTError
from app.realtime import process_realtime_frame
from app.security import decode_token


sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")


def create_socket_app(fastapi_app: FastAPI) -> socketio.ASGIApp:
    return socketio.ASGIApp(sio, other_asgi_app=fastapi_app, socketio_path="ws/analytics")


@sio.event
async def connect(sid, environ, auth):
    token = None
    if isinstance(auth, dict):
        token = auth.get("token")
    if not token:
        return False
    try:
        payload = decode_token(token)
    except PyJWTError:
        return False
    if payload.get("role") != "admin":
        return False
    await sio.save_session(sid, {"user": payload.get("sub")})
    return True


@sio.event
async def disconnect(sid):
    return None


@sio.event
async def frame(sid, data):
    try:
        encoded_frame, counts = process_realtime_frame(data)
        await sio.emit("result", {"frame": encoded_frame, "counts": counts}, to=sid)
    except Exception:
        return None


async def emit_event(event: str, payload: dict):
    await sio.emit(event, payload)
