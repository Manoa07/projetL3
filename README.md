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
pip install PyQt6 qasync requests opencv-python mediapipe mtcnn keras-facenet numpy
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

## Remarques de cohérence

- Les imports backend sont écrits pour être exécutés depuis `Backend/app`.
- `frontend/services/presenceTheard.py` conserve l'ancien nom pour compatibilité, mais expose maintenant `PresenceThread`.
- Les schémas Pydantic ont été normalisés sur `from_attributes=True`.
