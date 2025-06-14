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


from fastapi import FastAPI , WebSocket
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
    print("✅ WebSocket accepted !")
    while True:
        try:
            data = await websocket.receive_bytes()
            np_arr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                print("Frame décodée nulle")
                continue
            print(f"Image reçue: {frame.shape}")
            latest_frame = frame
        except Exception as e:
            print(f"Erreur WebSocket: {e}")

@app.get("/video_feed")
async def video_feed():
    boundary = "frame"

    async def generate():
        global latest_frame
        while True:
            await asyncio.sleep(0.05)
            if latest_frame is None:
                continue
            try:
                ret, jpeg = cv2.imencode(".jpg", latest_frame)
                if not ret:
                    print("Erreur encodage JPEG")
                    continue
                frame_bytes = jpeg.tobytes()
                print(f"Envoi image de taille {len(frame_bytes)} octets")  # <--- log
                yield (
                    f"--{boundary}\r\n"
                    "Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(frame_bytes)}\r\n\r\n"
                ).encode() + frame_bytes + b"\r\n"
            except Exception as e:
                print(f"Erreur dans generate: {e}")

    headers = {"Content-Type": f"multipart/x-mixed-replace; boundary={boundary}"}
    return StreamingResponse(generate(), headers=headers)


