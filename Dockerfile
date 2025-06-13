FROM python:3.10-slim

# Installer les dépendances système nécessaires pour OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers (dont main.py et start.sh)
COPY . .

# Donner les droits d’exécution au script start.sh
RUN chmod +x start.sh

# Lancer le script start.sh
CMD ["./start.sh"]
