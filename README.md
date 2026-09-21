# Système de surveillance vidéo intelligent et de présence

Projet composé de deux parties:
- `Backend`: API FastAPI pour les élèves, cours, présence, examen, surveillance et caméra.
- `frontend`: application PyQt6 pour l'interface de supervision et de pointage.

## Prérequis

- Python 3.12 recommandé comme version stable du projet
- Python 3.13 compatible seulement si les outils de compilation Microsoft C++ Build Tools sont installés
- PostgreSQL installé et démarré localement
- Un environnement virtuel Python dédié au projet
- Les dépendances Python du backend et du frontend

Le projet fonctionne sans Docker. PostgreSQL est le seul service externe requis.

### Modèles locaux requis

La surveillance vidéo utilise également les fichiers binaires suivants, qui ne sont pas versionnés par Git :
- `frontend/models/pose_landmarker.task`: extraction des points du corps avec MediaPipe.
- `models/posture_classifier.pkl`: classification des postures suspectes.
- `frontend/models/weights/yolov8n.pt`: détection des objets interdits avec YOLO.

Ces fichiers sont ignorés par `.gitignore` et doivent être présents localement avant de lancer la surveillance.

## Installation

### 1) Créer l’environnement virtuel

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Installer les dépendances

Option recommandée pour le projet complet :

```powershell
python -m pip install -r requirements.txt
```

Ou installation séparée si besoin :

```powershell
python -m pip install -r requirements-backend.txt
python -m pip install -r requirements-frontend.txt
```

> Important : les dépendances ont été vérifiées avant le push Git. La version stable recommandée pour ce projet reste Python 3.12. Sous Python 3.13, le paquet psycopg2-binary peut nécessiter l’installation des Microsoft C++ Build Tools pour compiler localement.

### 3) Configurer l’environnement local

Copie `.env.example` vers `.env`, puis adapte les identifiants PostgreSQL.

```powershell
Copy-Item .env.example .env
```

## Checklist avant push Git

Avant de faire un push sur Git, vérifie impérativement :

```powershell
git status --short
```

Vérifications à faire :
- `.env` n’est pas suivi ni envoyé
- les modèles binaires `.task`, `.pkl`, `.pt` ne sont pas ajoutés
- les fichiers de logs ne sont pas envoyés
- la version de Python utilisée est bien compatible avec les requirements
- les dépendances installées correspondent aux versions listées dans les fichiers de requirements

> En particulier, la version `numpy` a été alignée sur une variante compatible avec Python 3.13 pour éviter les échecs de build sur Windows.

Exemple de fichiers ignorés attendus :
- `.env`
- `*.task`
- `*.pkl`
- `*.pt`
- `*.log`

## Détection des postures et des gestes

La surveillance combine deux traitements sur chaque caméra :
1. YOLO détecte les objets interdits et ajoute les alertes correspondantes.
2. MediaPipe PoseLandmarker extrait les points du corps, puis le classifieur
   local reconnaît les postures suspectes entraînées dans `frontend/posture_detection/dataset_postures`.

Une posture est confirmée par un vote sur plusieurs images consécutives afin
de limiter les faux positifs. Le modèle de posture peut être régénéré depuis
le dataset existant :

```powershell
.venv\Scripts\python.exe frontend\posture_detection\train_model.py
```

### Détection YOLOv8

La surveillance en direct utilise automatiquement `frontend/models/weights/yolov8n.pt` lorsque
Ultralytics est installé. L’analyse de posture MediaPipe reste active et reçoit
la frame originale; les annotations YOLO sont ajoutées uniquement à l’image
affichée.

Pour choisir un autre modèle ou un autre appareil :

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
