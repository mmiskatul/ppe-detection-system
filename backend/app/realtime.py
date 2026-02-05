import cv2
import base64
from ultralytics import YOLO
from collections import Counter
import numpy as np

model = YOLO("best.pt")
if not model.names:
    model.names = {0: "Mask", 1: "Helmet", 2: "Vest", 3: "Boots", 4: "Person"}

class_names = model.names

def process_realtime_frame(frame_bytes_base64):
    img_bytes = base64.b64decode(frame_bytes_base64)
    np_img = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    results = model(frame)
    annotated_frame = results[0].plot()  # Keep colors

    _, buffer = cv2.imencode(".jpg", annotated_frame)
    encoded_frame = base64.b64encode(buffer).decode("utf-8")

    cls_ids = [int(c) for c in results[0].boxes.cls.cpu().numpy()]
    counts = Counter([class_names[i] for i in cls_ids])

    return encoded_frame, dict(counts)
