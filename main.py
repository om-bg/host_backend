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

#-------------------------- Ca marche sans detection --------------------------------------------#
# from fastapi import FastAPI , WebSocket
# from fastapi.responses import StreamingResponse
# import cv2
# import numpy as np
# import asyncio

# app = FastAPI()
# latest_frame = None
# @app.get("/")
# async def root():
#     return {"message": "Host OK"}

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     global latest_frame
#     await websocket.accept()
#     print("✅ WebSocket accepted !")
#     while True:
#         try:
#             data = await websocket.receive_bytes()
#             np_arr = np.frombuffer(data, np.uint8)
#             frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#             if frame is None:
#                 print("Frame décodée nulle")
#                 continue
#             print(f"Image reçue: {frame.shape}")
#             latest_frame = frame
#         except Exception as e:
#             print(f"Erreur WebSocket: {e}")

# @app.get("/video_feed")
# async def video_feed():
#     boundary = "frame"

#     async def generate():
#         global latest_frame
#         while True:
#             await asyncio.sleep(0.05)
#             if latest_frame is None:
#                 continue
#             try:
#                 ret, jpeg = cv2.imencode(".jpg", latest_frame)
#                 if not ret:
#                     print("Erreur encodage JPEG")
#                     continue
#                 frame_bytes = jpeg.tobytes()
#                 print(f"Envoi image de taille {len(frame_bytes)} octets")  # <--- log
#                 yield (
#                     f"--{boundary}\r\n"
#                     "Content-Type: image/jpeg\r\n"
#                     f"Content-Length: {len(frame_bytes)}\r\n\r\n"
#                 ).encode() + frame_bytes + b"\r\n"
#             except Exception as e:
#                 print(f"Erreur dans generate: {e}")

#     headers = {"Content-Type": f"multipart/x-mixed-replace; boundary={boundary}"}
#     return StreamingResponse(generate(), headers=headers)

# from fastapi import FastAPI, WebSocket
# from fastapi.responses import StreamingResponse
# import cv2
# import numpy as np
# import asyncio

# app = FastAPI()
# latest_frame = None

# # Initialiser le détecteur de personnes HOG
# hog = cv2.HOGDescriptor()
# hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# @app.get("/")
# async def root():
#     return {"message": "Host OK"}

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     global latest_frame
#     await websocket.accept()
#     print("✅ WebSocket accepted !")
#     while True:
#         try:
#             data = await websocket.receive_bytes()
#             np_arr = np.frombuffer(data, np.uint8)
#             frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#             if frame is None:
#                 print("❌ Frame décodée nulle")
#                 continue

#             # 🔍 Détection des personnes
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             boxes, weights = hog.detectMultiScale(gray, winStride=(8, 8))

#             # Dessiner les rectangles sur l'image originale
#             for (x, y, w, h) in boxes:
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

#             latest_frame = frame
#         except Exception as e:
#             print(f"⚠️ Erreur WebSocket: {e}")

# @app.get("/video_feed")
# async def video_feed():
#     boundary = "frame"

#     async def generate():
#         global latest_frame
#         while True:
#             await asyncio.sleep(0.05)  # rythme d’envoi ~20 fps max
#             if latest_frame is None:
#                 continue
#             try:
#                 ret, jpeg = cv2.imencode(".jpg", latest_frame)
#                 if not ret:
#                     print("❌ Erreur encodage JPEG")
#                     continue
#                 frame_bytes = jpeg.tobytes()
#                 yield (
#                     f"--{boundary}\r\n"
#                     "Content-Type: image/jpeg\r\n"
#                     f"Content-Length: {len(frame_bytes)}\r\n\r\n"
#                 ).encode() + frame_bytes + b"\r\n"
#             except Exception as e:
#                 print(f"⚠️ Erreur dans generate: {e}")

#     headers = {"Content-Type": f"multipart/x-mixed-replace; boundary={boundary}"}
#     return StreamingResponse(generate(), headers=headers)

from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import asyncio
from imutils.object_detection import non_max_suppression

app = FastAPI()

latest_frame = None

# Initialiser le détecteur HOG
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

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
                frame = latest_frame.copy()

                # 🔍 Agrandir temporairement l'image pour meilleure détection
                upscaled = cv2.resize(frame, (640, 480))

                # Détection de personnes
                (rects, weights) = hog.detectMultiScale(upscaled, winStride=(4, 4), padding=(8, 8), scale=1.05)

                # Suppression des doublons (non-max suppression)
                rects_np = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
                pick = non_max_suppression(rects_np, probs=None, overlapThresh=0.65)

                # Mise à l'échelle vers l'image originale
                scale_x = frame.shape[1] / 640
                scale_y = frame.shape[0] / 480
                for (xA, yA, xB, yB) in pick:
                    x1 = int(xA * scale_x)
                    y1 = int(yA * scale_y)
                    x2 = int(xB * scale_x)
                    y2 = int(yB * scale_y)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Encodage JPEG
                ret, jpeg = cv2.imencode(".jpg", frame)
                if not ret:
                    continue

                frame_bytes = jpeg.tobytes()
                yield (
                    f"--{boundary}\r\n"
                    "Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(frame_bytes)}\r\n\r\n"
                ).encode() + frame_bytes + b"\r\n"

            except Exception as e:
                print(f"❌ Erreur stream: {e}")
                break

    headers = {"Content-Type": f"multipart/x-mixed-replace; boundary={boundary}"}
    return StreamingResponse(generate(), headers=headers)


