# import cv2
# import numpy as np
# from fastapi import FastAPI, WebSocket
# from fastapi.responses import StreamingResponse
# from ultralytics import YOLO
# import asyncio
# import uvicorn

# app = FastAPI()
# model = YOLO('yolov8n.pt')  # Remplacez par yolov8vn.pt

# class ESP32CamStream:
#     def __init__(self):
#         self.cap = None
#         self.stream_url = "http://192.168.137.97/mjpeg"  # Utilise /video au lieu de /mjpeg
        
#     async def connect(self):
#         self.cap = cv2.VideoCapture(self.stream_url)
#         if not self.cap.isOpened():
#             raise ConnectionError("Impossible de se connecter au flux ESP32-CAM")
    
#     async def get_frame(self):
#         ret, frame = self.cap.read()
#         if not ret:
#             await self.connect()  # Reconnexion si nécessaire
#             return None
#         return frame

# stream = ESP32CamStream()

# @app.on_event("startup")
# async def startup_event():
#     await stream.connect()

# async def generate_frames():
#     while True:
#         frame = await stream.get_frame()
#         if frame is None:
#             await asyncio.sleep(0.1)
#             continue
            
#         # Détection YOLOv8
#         results = model.track(frame, persist=True)  # Tracking pour meilleure continuité
        
#         # Annotation
#         for r in results:
#             boxes = r.boxes.xyxy.cpu().numpy()
#             confs = r.boxes.conf.cpu().numpy()
#             cls_ids = r.boxes.cls.cpu().numpy().astype(int)
            
#             for box, conf, cls_id in zip(boxes, confs, cls_ids):
#                 x1, y1, x2, y2 = map(int, box)
#                 label = f"{model.names[cls_id]} {conf:.2f}"
                
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.putText(frame, label, (x1, y1-10), 
#                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
#         # Encodage
#         _, buffer = cv2.imencode('.jpg', frame)
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# @app.get("/processed_stream")
# async def video_feed():
#     return StreamingResponse(generate_frames(),
#                            media_type="multipart/x-mixed-replace; boundary=frame")

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             frame = await stream.get_frame()
#             if frame is None:
#                 await asyncio.sleep(0.1)
#                 continue
                
#             # Traitement identique à generate_frames()
#             results = model.track(frame, persist=True)
#             # ... [même code d'annotation] ...
            
#             # Envoi via WebSocket
#             _, buffer = cv2.imencode('.jpg', frame)
#             await websocket.send_bytes(buffer.tobytes())
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         await websocket.close()

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

###################################### bien marcher avec plus de latence ################################
# import cv2
# import numpy as np
# from fastapi import FastAPI, WebSocket
# from fastapi.responses import StreamingResponse
# from ultralytics import YOLO
# import uvicorn
# import asyncio

# app = FastAPI()
# model = YOLO('yolov8n.pt')  # Utilisez votre modèle yolov8vn.pt

# class VideoProcessor:
#     def __init__(self):
#         self.stream_url = "http://192.168.137.112/video"
#         self.cap = cv2.VideoCapture(self.stream_url)
#         self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#         self.cap.set(cv2.CAP_PROP_FPS, 15)
        
#     async def process_frame(self):
#         ret, frame = self.cap.read()
#         if not ret:
#             return None
        
#         # Détection
#         results = model(frame)
        
#         # Annotation
#         for r in results:
#             boxes = r.boxes.xyxy.cpu().numpy()
#             confs = r.boxes.conf.cpu().numpy()
#             cls_ids = r.boxes.cls.cpu().numpy().astype(int)
            
#             for box, conf, cls_id in zip(boxes, confs, cls_ids):
#                 x1, y1, x2, y2 = map(int, box)
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.putText(frame, f"{model.names[cls_id]} {conf:.2f}",
#                            (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
#         return frame

# processor = VideoProcessor()

# @app.get("/video_feed")
# async def video_feed():
#     async def generate():
#         while True:
#             frame = await processor.process_frame()
#             if frame is None:
#                 continue
#             _, buffer = cv2.imencode('.jpg', frame)
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
#     return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             frame = await processor.process_frame()
#             if frame is None:
#                 await asyncio.sleep(0.1)
#                 continue
#             _, buffer = cv2.imencode('.jpg', frame)
#             await websocket.send_bytes(buffer.tobytes())
#             await asyncio.sleep(0.05)  # ~20 FPS
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         await websocket.close()

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

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
