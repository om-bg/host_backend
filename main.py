# from fastapi.responses import StreamingResponse
# from fastapi import FastAPI
# import cv2
# import numpy as np
# import asyncio

# app = FastAPI()

# # Initialiser le détecteur HOG
# hog = cv2.HOGDescriptor()
# hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# # Flux vidéo (ex: ngrok ESP32-CAM)
# stream_url = "https://9a0f-105-69-217-81.ngrok-free.app/video"
# cap = cv2.VideoCapture(stream_url)

# def detect_people(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     boxes, _ = hog.detectMultiScale(gray, winStride=(8, 8))
#     for (x, y, w, h) in boxes:
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         cv2.putText(frame, "Person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5, (0, 255, 0), 2)
#     return frame
# @app.get("/")
# async def root():
#     return {"message": "Host OK"}


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

#             yield (
#                 f"--{boundary}\r\n"
#                 "Content-Type: image/jpeg\r\n\r\n"
#             ).encode() + buffer.tobytes() + b"\r\n"

#     return StreamingResponse(generate(), media_type=f"multipart/x-mixed-replace; boundary={boundary}")


from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import asyncio

app = FastAPI()
latest_frame = None
@app.get("/")
async def root():
    return {"message": "Host OK"}
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global latest_frame
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        np_arr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        latest_frame = frame

@app.get("/video_feed")
async def video_feed():
    boundary = "frame"

    async def generate():
        global latest_frame
        while True:
            await asyncio.sleep(0.05)
            if latest_frame is None:
                continue
            _, jpeg = cv2.imencode(".jpg", latest_frame)
            yield (
                f"--{boundary}\r\n"
                "Content-Type: image/jpeg\r\n"
                f"Content-Length: {len(jpeg)}\r\n\r\n"
            ).encode() + jpeg.tobytes() + b"\r\n"

    headers = {"Content-Type": f"multipart/x-mixed-replace; boundary={boundary}"}
    return StreamingResponse(generate(), headers=headers)

