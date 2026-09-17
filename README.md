# Système de surveillance vidéo intelligent et de présence

Projet composé de deux parties:
- `Backend`: API FastAPI pour les élèves, cours, présence, examen, surveillance et caméra.
- `frontend`: application PyQt6 pour l'interface de supervision et de pointage.

## Prérequis

- Python 3.12 recommandé (TensorFlow n'est pas disponible avec Python 3.14)
- PostgreSQL
- Les dépendances Python du backend et du frontend

## Installation

### Backend

```bash
cd Backend/app
../../.venv/bin/python3.12 -m pip install -r ../../requirements.txt
```

### Frontend

```bash
cd frontend
pip install PyQt6 qasync requests opencv-python mediapipe mtcnn keras-facenet numpy ultralytics
```

## Configuration

Le backend utilise exclusivement PostgreSQL. Définis obligatoirement la variable
`DATABASE_URL` avant le lancement, par exemple:

```bash
export DATABASE_URL="postgresql+psycopg2://utilisateur:mot_de_passe@localhost:5432/surveillance"
```

Toute URL qui n'utilise pas PostgreSQL est refusée par le backend.

Les fichiers téléversés pour les élèves sont enregistrés dans:
- `Backend/app/upload/eleve_upload`

## Lancement

### Backend

Depuis `Backend/app`:

```bash
../../.venv/bin/python3.12 -m uvicorn main:app --reload
```

### Frontend

Depuis `frontend`:

```bash
python main.py
```

## Structure

- `Backend/app/main.py`: point d'entrée FastAPI
- `Backend/app/routes`: routes HTTP
- `Backend/app/services`: logique métier
- `Backend/app/models`: modèles SQLAlchemy
- `Backend/app/schema`: schémas Pydantic
- `frontend/main.py`: point d'entrée PyQt6
- `frontend/interface`: écrans principaux
- `frontend/views`: vues secondaires
- `frontend/services`: threads et services réseau

### Détection YOLOv8

La surveillance en direct utilise automatiquement `frontend/models/weights/yolov8n.pt` lorsque
Ultralytics est installé. L’analyse de posture MediaPipe reste active et reçoit
la frame originale; les annotations YOLO sont ajoutées uniquement à l’image
affichée.

Pour choisir un autre modèle ou un autre appareil:

```powershell
$env:YOLO_MODEL_PATH = "frontend/models/weights/yolov8m.pt"
$env:YOLO_DEVICE = "cpu"
$env:YOLO_CONFIDENCE = "0.25"
$env:EXAM_ID = "1"
$env:YOLO_FORBIDDEN_OBJECTS = "cell phone,laptop,tablet,book,backpack,bottle"
$env:SURVEILLANCE_API_URL = "http://127.0.0.1:8000/surveillance/object-alert"
cd frontend
python main.py
```

`EXAM_ID` doit correspondre a un examen existant dans le backend. Lorsqu'un objet
interdit est detecte, l'alerte est affichee dans le fil live et enregistree via
`POST /surveillance/object-alert` avec son niveau de confiance.

Si le modèle, Ultralytics ou sa configuration sont indisponibles, la surveillance
continue avec le pipeline MediaPipe existant.

## Remarques de cohérence

- Les imports backend sont écrits pour être exécutés depuis `Backend/app`.
- `frontend/services/presenceTheard.py` conserve l'ancien nom pour compatibilité, mais expose maintenant `PresenceThread`.
- Les schémas Pydantic ont été normalisés sur `from_attributes=True`.
