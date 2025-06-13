# Étape 1 : base image
FROM python:3.10-slim

# Étape 2 : répertoires et variables
WORKDIR /app

# Étape 3 : installer les dépendances système
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Étape 4 : copier les fichiers et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Étape 5 : lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
