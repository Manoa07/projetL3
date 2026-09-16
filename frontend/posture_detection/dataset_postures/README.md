# Dataset pour l'Entraînement des Postures Suspectes

Ce dossier permet d'entraîner le modèle d'intelligence artificielle sur vos propres images ou photos de caméra.

## Structure des classes

Placez vos images (`.jpg`, `.png`) dans les sous-dossiers correspondants :

- `normal/` : Étudiant assis normalement, regardant sa copie ou le tableau.
- `regarde_voisin_gauche/` : Étudiant tournant la tête vers la gauche pour regarder la copie du voisin.
- `regarde_voisin_droite/` : Étudiant tournant la tête vers la droite pour regarder la copie du voisin.
- `main_sous_table/` : Étudiant ayant une ou deux mains cachées sous la table.
- `regarde_antiseche/` : Étudiant la tête penchée très bas vers ses jambes ou une feuille cachée.
- `bras_vers_voisin/` : Étudiant tendant le bras vers son voisin.

> **Note importante** : Conformément aux consignes, la détection de téléphone a été retirée du système.

## Méthode 1 : Enregistreur Automatique Guidé par Webcam (Recommandée)

C'est la méthode la plus rapide et la plus précise : en **30 secondes**, vous obtenez 300 exemples adaptés directement à votre caméra et votre éclairage.

### Comment l'utiliser ?
1. Lancez simplement le script :
   ```bash
   python frontend/posture_detection/collect_dataset.py
   ```
2. Une fenêtre s'ouvre avec le retour caméra et un squelette en temps réel :
   - **Étape 1** : "Posture normale" (compte à rebours 4s pour vous installer, puis enregistrement automatique de 60 images).
   - **Étape 2** : "Regarde voisin gauche" (compte à rebours, enregistrement de 60 images).
   - **Étape 3** : "Regarde voisin droite" (compte à rebours, enregistrement de 60 images).
   - **Étape 4** : "Mains sous la table" (compte à rebours, enregistrement de 60 images).
   - **Étape 5** : "Regarde antisèche / jambes" (compte à rebours, enregistrement de 60 images).
3. Le script remplit automatiquement les sous-dossiers et écrit directement les coordonnées dans `landmarks_dataset.csv`.
4. Lancez ensuite l'entraînement :
   ```bash
   python frontend/posture_detection/train_model.py
   ```

---

## Méthode Manuelle (Alternative avec vos propres photos)

Si vous préférez ajouter des photos manuellement :
1. Déposez vos photos (`.jpg`, `.png`) dans les sous-dossiers correspondants.
2. Extrayez les caractéristiques :
   ```bash
   python frontend/posture_detection/extract_dataset.py
   ```
3. Entraînez le modèle :
   ```bash
   python frontend/posture_detection/train_model.py
   ```


