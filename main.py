from fastapi.responses import StreamingResponse
from fastapi import FastAPI
import cv2
import numpy as np
import asyncio

app = FastAPI()

# # Initialiser le détecteur HOG
# hog = cv2.HOGDescriptor()
# hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# # Flux vidéo (ex: ngrok ESP32-CAM)
# stream_url = "https://bff4-105-76-167-117.ngrok-free.app/video"
# cap = cv2.VideoCapture(stream_url)

# def detect_people(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     boxes, _ = hog.detectMultiScale(gray, winStride=(8, 8))
#     for (x, y, w, h) in boxes:
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         cv2.putText(frame, "Person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5, (0, 255, 0), 2)
#     return frame
@app.get("/")
async def root():
    return {"message": "Host OK"}


# @app.get("/video_feed")
# async def video_feed():
#     boundary = "frame"

#     async def generate():
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 await asyncio.sleep(0.05)
#                 continue

#             frame = detect_people(frame)
#             ret, buffer = cv2.imencode('.jpg', frame)
#             if not ret:
#                 continue

#             # Respect strict du format MJPEG
#             yield (
#                 f"--{boundary}\r\n"
#                 "Content-Type: image/jpeg\r\n"
#                 f"Content-Length: {len(buffer)}\r\n\r\n"
#             ).encode() + buffer.tobytes() + b"\r\n"

#     headers = {
#         "Content-Type": f"multipart/x-mixed-replace; boundary={boundary}"
#     }
#     return StreamingResponse(generate(), headers=headers)
