# Système de surveillance vidéo intelligent et de présence

Projet composé de deux parties:
- `Backend`: API FastAPI pour les élèves, cours, présence, examen, surveillance et caméra.
- `frontend`: application PyQt6 pour l'interface de supervision et de pointage.

## Prérequis

- Python 3.10+ recommandé
- PostgreSQL
- Les dépendances Python du backend et du frontend

## Installation

### Backend

```bash
cd Backend/app
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic
```

### Frontend

```bash
cd frontend
pip install PyQt6 qasync requests opencv-python mediapipe mtcnn keras-facenet numpy
```

## Configuration

Le backend utilise la variable `DATABASE_URL` définie dans [Backend/app/DB/database.py](/home/manoa/Bureau/projetL3/Backend/app/DB/database.py).
Vérifie que l'URL PostgreSQL correspond à ton environnement local.

Les fichiers téléversés pour les élèves sont enregistrés dans:
- `Backend/app/upload/eleve_upload`

## Lancement

### Backend

Depuis `Backend/app`:

```bash
uvicorn main:app --reload
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
