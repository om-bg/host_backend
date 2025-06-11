FROM python:3.10-slim

# Dépendances système pour OpenCV et PyTorch
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg && \
    apt-get clean

WORKDIR /app

COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port utilisé par uvicorn
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
