# Système de surveillance vidéo intelligent et de présence

Projet composé de deux parties:
- `Backend`: API FastAPI pour les élèves, cours, présence, examen, surveillance et caméra.
- `frontend`: application PyQt6 pour l'interface de supervision et de pointage.

## Prérequis

- Python 3.11 ou 3.12
- PostgreSQL installé et démarré localement
- Les dépendances Python du backend et du frontend

Le projet fonctionne sans Docker. PostgreSQL est le seul service externe requis.

La surveillance vidéo utilise également les modèles locaux suivants:
- `frontend/models/pose_landmarker.task`: extraction des points du corps avec MediaPipe.
- `models/posture_classifier.pkl`: classification des postures suspectes.
- `frontend/models/weights/yolov8n.pt`: détection des objets interdits avec YOLO.

Les fichiers binaires de modèles sont ignorés par Git. Ils doivent donc être
présents localement avant de lancer la surveillance.

## Installation

### Installation

Depuis la racine du projet, crée un environnement virtuel puis installe les deux
groupes de dépendances:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-backend.txt
python -m pip install -r requirements-frontend.txt
```

Copie `.env.example` vers `.env`, puis adapte les identifiants PostgreSQL.

### Base de données

Crée une base PostgreSQL locale correspondant à `DATABASE_URL`:

```bash
createdb -U postgres surveillance
```

Sous Windows, tu peux aussi créer la base avec pgAdmin. Le backend crée les tables
au démarrage.

## Configuration

Le backend utilise exclusivement PostgreSQL. Avec PostgreSQL local, la valeur est:

```bash
DATABASE_URL=postgresql://utilisateur:mot_de_passe@localhost:5432/surveillance
```

Toute URL qui n'utilise pas PostgreSQL est refusée par le backend.

Les fichiers téléversés pour les élèves sont enregistrés dans:
- `Backend/app/upload/eleve_upload`

## Lancement

### Lancement local

Dans un terminal PowerShell, lance le backend:

```powershell
.\scripts\run-backend.ps1
```

Dans un second terminal PowerShell, lance le frontend:

```powershell
.\scripts\run-frontend.ps1
```

L'API est disponible sur `http://127.0.0.1:8000`.

### Caméras locales

Le script frontend utilise par défaut deux caméras:
- salle A: caméra intégrée de l'ordinateur, index `1`;
- salle B: webcam USB, index `0`.

La configuration est définie par `CAMERA_SOURCES`, avec les sources séparées
par des virgules. Pour inverser les deux caméras:

```powershell
$env:CAMERA_SOURCES = "0,1"
.\scripts\run-frontend.ps1
```

Une source peut aussi être un flux réseau de smartphone compatible OpenCV:

```powershell
$env:CAMERA_SOURCES = "1,http://192.168.1.20:8080/video"
.\scripts\run-frontend.ps1
```

Le téléphone et l'ordinateur doivent être connectés au même réseau local.

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

## Interface utilisateur

- La fenêtre principale utilise une taille standard de `1280 x 800` pixels,
	avec une taille minimale de `1100 x 700`.
- Les pages Présence et Surveillance utilisent une barre latérale harmonisée,
	avec une navigation claire et des états actifs visibles.
- La page de surveillance affiche les flux des salles dans une grille compacte,
	sans défilement vertical de la zone vidéo, avec un fil d'alertes visible.
- Les fenêtres secondaires, tableaux et historiques utilisent un thème clair.
- Les tableaux sont en lecture seule, occupent la largeur disponible et gardent
	une hauteur stable; leurs lignes supplémentaires sont accessibles par leur
	défilement interne.
- La gestion des élèves propose un compteur, un état vide et des actions
	clairement différenciées pour l'historique, la modification et la suppression.

## Détection des postures et des gestes

La surveillance combine deux traitements sur chaque caméra:
1. YOLO détecte les objets interdits et ajoute les alertes correspondantes.
2. MediaPipe PoseLandmarker extrait les points du corps, puis le classifieur
	 local reconnaît les postures suspectes entraînées dans
	 `frontend/posture_detection/dataset_postures`.

Une posture est confirmée par un vote sur plusieurs images consécutives afin
de limiter les faux positifs. Le modèle de posture peut être régénéré depuis
le dataset existant:

```powershell
.venv\Scripts\python.exe frontend\posture_detection\train_model.py
```

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

`EXAM_ID` doit correspondre à un examen existant dans le backend. Lorsqu'un objet
interdit est détecté, l'alerte est affichée dans le fil live et enregistrée via
`POST /surveillance/object-alert` avec son niveau de confiance.

Si le modèle, Ultralytics ou sa configuration sont indisponibles, la surveillance
continue avec le pipeline MediaPipe existant.

## Remarques de cohérence

- Les scripts `scripts/run-backend.ps1` et `scripts/run-frontend.ps1` configurent
	automatiquement les répertoires de lancement.
- `frontend/services/presenceTheard.py` conserve l'ancien nom pour compatibilité, mais expose maintenant `PresenceThread`.
- Les schémas Pydantic ont été normalisés sur `from_attributes=True`.
