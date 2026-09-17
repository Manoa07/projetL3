FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    API_BASE_URL=http://backend:8000

WORKDIR /app

# Dépendances système pour PyQt6 et OpenCV sur Ubuntu/Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libx11-xcb1 \
    libegl1 \
    libgl1 \
    libfontconfig1 \
    libdbus-1-3 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-frontend.txt /tmp/requirements-frontend.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements-frontend.txt

# Copie de l'application frontend
COPY frontend /app

# Crée le dossier des modèles IA visibles depuis le volume monté
RUN mkdir -p /app/models/weights

# Note de fonctionnement :
# - Linux desktop : lancer avec X11 forwarding
#   docker run --rm -it \
#     -e DISPLAY=$DISPLAY \
#     -v /tmp/.X11-unix:/tmp/.X11-unix \
#     --device /dev/video0:/dev/video0 \
#     projetl3-frontend
#
# - Environnement headless / CI : le conteneur PyQt6 ne peut pas afficher l'interface
#   sans un serveur X11 ou un framebuffer virtuel ; il faut donc utiliser un mode
#   "headless" ou un display virtualisé.

CMD ["python", "main.py"]
