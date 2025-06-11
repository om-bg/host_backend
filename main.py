import cv2
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
import uvicorn
import asyncio

app = FastAPI()
model = YOLO('yolov8n.pt')  # ton modèle YOLO

class VideoProcessor:
    def __init__(self):
        self.stream_url = "http://192.168.137.38/video"
        self.cap = cv2.VideoCapture(self.stream_url)
        self.latest_frame = None
        self.running = True

    async def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                await asyncio.sleep(0.05)
                continue

            # Détection YOLO
            results = model(frame)
            for r in results:
                boxes = r.boxes.xyxy.cpu().numpy()
                confs = r.boxes.conf.cpu().numpy()
                cls_ids = r.boxes.cls.cpu().numpy().astype(int)
                for box, conf, cls_id in zip(boxes, confs, cls_ids):
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{model.names[cls_id]} {conf:.2f}",
                                (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            self.latest_frame = frame
            await asyncio.sleep(0.03)  # 30 FPS max

    async def get_latest_frame(self):
        return self.latest_frame

processor = VideoProcessor()

@app.on_event("startup")
async def start_video_task():
    asyncio.create_task(processor.update_frame())

@app.get("/video_feed")
async def video_feed():
    async def generate():
        while True:
            frame = await processor.get_latest_frame()
            if frame is None:
                await asyncio.sleep(0.05)
                continue
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            frame = await processor.get_latest_frame()
            if frame is None:
                await asyncio.sleep(0.05)
                continue
            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send_bytes(buffer.tobytes())
            await asyncio.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
