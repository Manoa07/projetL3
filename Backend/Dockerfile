FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dépendances système requises pour PostgreSQL + OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-backend.txt /tmp/requirements-backend.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements-backend.txt

# Copie de l'application
COPY Backend/app /app

# Répertoire de stockage des uploads
RUN mkdir -p /app/upload/eleve_upload

# Création d'un utilisateur non-root
RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /home/app app && \
    chown -R app:app /app /home/app

USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
