# Module de Détection des Postures Suspectes par IA

Ce module remplace l'ancien système de règles mathématiques manuelles par un **modèle d'Intelligence Artificielle (Machine Learning)** entraîné directement sur les articulations du corps (MediaPipe PoseLandmarker).

> **Note** : La détection de téléphone a été intégralement supprimée du système.

---

## Architecture du Dossier `frontend/posture_detection/`

```text
posture_detection/
├── README.md               # Le présent guide d'utilisation
├── classifier.py           # Extracteur de 66 caractéristiques invariantes + classifieur ML
├── mouvement.py            # Analyse des alertes IA + chuchotement + score de suspicion
├── posture_detection.py    # Détection des flux vidéo et tracking des étudiants
├── collect_dataset.py      # Méthode 1 : Collecteur automatique par webcam guidée (recommandé)
├── extract_dataset.py      # Méthode manuelle : Extraction des landmarks depuis des photos
├── train_model.py          # Script d'entraînement et d'évaluation du modèle ML
└── dataset_postures/       # Dossier contenant les données d'apprentissage
    ├── normal/
    ├── regarde_voisin_gauche/
    ├── regarde_voisin_droite/
    ├── main_sous_table/
    ├── regarde_antiseche/
    └── landmarks_dataset.csv
```

---

## Guide Rapide : Les Étapes à Suivre

### Étape 1 : Collecter les données (Méthode Recommandée)

Pour enregistrer vos postures directement avec votre webcam :
```powershell
python frontend/posture_detection/collect_dataset.py
```
- Le script affiche votre webcam avec le squelette MediaPipe en temps réel.
- Un compte à rebours de **4 secondes** vous laisse le temps de vous mettre en position pour chaque posture.
- Le script enregistre automatiquement **60 images et 60 squelettes** par posture :
  1. Posture normale (assis face à la feuille)
  2. Regarde voisin gauche (tête tournée à gauche)
  3. Regarde voisin droite (tête tournée à droite)
  4. Mains sous la table
  5. Regarde antisèche / jambes (tête baissée)
- En **30 secondes**, vous obtenez 300 exemples prêts pour l'apprentissage.

---

### Étape 2 : Entraîner le Modèle IA

Une fois la collecte terminée (ou après avoir ajouté de nouveaux exemples) :
```powershell
python frontend/posture_detection/train_model.py
```
- Le script charge `landmarks_dataset.csv`.
- Il entraîne un classifieur **Random Forest** robuste.
- Il évalue le modèle sur un jeu de test et affiche le score de précision (accuracy).
- Il sauvegarde automatiquement le modèle entraîné dans :  
  `models/posture_classifier.pkl`

---

### Étape 3 : Lancer la Surveillance

Le modèle entraîné est **instantanément prêt**. Il vous suffit de démarrer l'application :
```powershell
python main.py
```
Puis activez la surveillance vidéo :
- L'IA analyse chaque étudiant à chaque image.
- Si une posture suspecte est détectée avec plus de 60% de certitude, l'alerte apparaît directement dans l'interface PyQt6 avec l'heure exacte.

---

## 🔄 Comment Augmenter la Précision du Modèle ?

Pour que le modèle soit encore plus performant en conditions réelles (différentes personnes, habits, éclairages) :
1. Faites passer **2 ou 3 personnes différentes** devant le collecteur :
   ```powershell
   python frontend/posture_detection/collect_dataset.py
   ```
   *(Les nouvelles données s'ajoutent automatiquement à celles déjà existantes dans le CSV).*
2. Relancez l'entraînement :
   ```powershell
   python frontend/posture_detection/train_model.py
   ```
Plus le nombre d'exemples augmente (ex: 600, 1000 exemples), plus le modèle devient précis et insensible aux faux positifs !
