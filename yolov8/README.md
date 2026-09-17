# Detection YOLOv8

Prototype de detection d'objets avec YOLOv8 et OpenCV.

## Installation

Python 3.10 ou 3.11 est recommande.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Le fichier `yolov8n.pt` est le modele utilise par defaut. Il se trouve dans `../frontend/models/weights/`.

## Utilisation

Lancer la detection avec la camera :

```powershell
python main.py --mode camera
```

Tester une image et enregistrer le resultat :

```powershell
python main.py --mode image --input chemin/vers/image.jpg --output resultat.jpg
```

Executer les tests :

```powershell
python -m pytest -q
```

Pour utiliser un autre modele :

```powershell
python main.py --mode image --model ../frontend/models/weights/yolov8n.pt --input chemin/vers/image.jpg --output resultat.jpg
```

## Contribution au projet GitHub

1. Cloner le depot et entrer dans son dossier.
2. Creer un environnement virtuel et installer `requirements.txt`.
3. Ajouter ou remplacer les fichiers du projet, puis executer les tests.
4. Creer une branche de fonctionnalite et ouvrir une pull request.

Le modele `yolov8n.pt` fait environ 6,5 Mo et peut etre versionne directement dans GitHub. Les environnements virtuels, caches et fichiers de sortie sont ignores par `.gitignore`.