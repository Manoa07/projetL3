"""
Script d'entraînement du modèle de détection de postures suspectes par Machine Learning.
Le modèle remplace les formules mathématiques en apprenant directement des exemples.
(Le téléphone est totalement exclu des postures).
"""

import os
import csv
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_CSV = os.path.join(CURRENT_DIR, "dataset_postures", "landmarks_dataset.csv")
OUTPUT_MODEL_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../../models"))
OUTPUT_MODEL_PATH = os.path.join(OUTPUT_MODEL_DIR, "posture_classifier.pkl")


def generate_baseline_dataset():
    """
    Génère des données synthétiques initiales réalistes pour permettre
    à l'application de fonctionner immédiatement même avant que l'utilisateur
    n'ait ajouté ses propres photos.
    Classes :
      - normal
      - Regarde voisin gauche
      - Regarde voisin droite
      - Main sous table
      - Regarde antiseche jambe
      - Bras vers voisin
    """
    np.random.seed(42)
    classes = [
        "normal",
        "Regarde voisin gauche",
        "Regarde voisin droite",
        "Main sous table",
        "Regarde antiseche jambe",
        "Bras vers voisin"
    ]

    samples_per_class = 150
    X_list = []
    y_list = []

    for label in classes:
        for _ in range(samples_per_class):
            # 33 points x 2 coordonnées = 66
            # On simule un squelette centré aux épaules (centre = 0, distance inter-épaules = 1.0)
            feats = np.zeros(66, dtype=np.float32)

            # Épaules : ls = (-0.5, 0.0), rs = (0.5, 0.0)
            feats[11 * 2] = -0.5 + np.random.normal(0, 0.03)
            feats[11 * 2 + 1] = 0.0 + np.random.normal(0, 0.03)
            feats[12 * 2] = 0.5 + np.random.normal(0, 0.03)
            feats[12 * 2 + 1] = 0.0 + np.random.normal(0, 0.03)

            # Hanches : lh = (-0.4, 1.3), rh = (0.4, 1.3)
            feats[23 * 2] = -0.4 + np.random.normal(0, 0.04)
            feats[23 * 2 + 1] = 1.3 + np.random.normal(0, 0.04)
            feats[24 * 2] = 0.4 + np.random.normal(0, 0.04)
            feats[24 * 2 + 1] = 1.3 + np.random.normal(0, 0.04)

            # Genoux
            feats[25 * 2] = -0.4 + np.random.normal(0, 0.05)
            feats[25 * 2 + 1] = 2.2 + np.random.normal(0, 0.05)
            feats[26 * 2] = 0.4 + np.random.normal(0, 0.05)
            feats[26 * 2 + 1] = 2.2 + np.random.normal(0, 0.05)

            # Poignets par défaut (sur la table devant le torse)
            # lw = (-0.3, 0.8), rw = (0.3, 0.8)
            lw_x, lw_y = -0.3 + np.random.normal(0, 0.05), 0.8 + np.random.normal(0, 0.05)
            rw_x, rw_y = 0.3 + np.random.normal(0, 0.05), 0.8 + np.random.normal(0, 0.05)

            # Nez par défaut (au centre au-dessus des épaules)
            nose_x, nose_y = 0.0 + np.random.normal(0, 0.05), -0.6 + np.random.normal(0, 0.05)

            # Variations selon la classe
            if label == "Regarde voisin gauche":
                # Tête tournée vers la gauche
                nose_x = -0.85 + np.random.normal(0, 0.08)
            elif label == "Regarde voisin droite":
                # Tête tournée vers la droite
                nose_x = 0.85 + np.random.normal(0, 0.08)
            elif label == "Main sous table":
                # Une des mains descend sous les hanches (y > 1.8)
                if np.random.rand() > 0.5:
                    lw_y = 1.9 + np.random.normal(0, 0.1)
                else:
                    rw_y = 1.9 + np.random.normal(0, 0.1)
            elif label == "Regarde antiseche jambe":
                # Tête très basse penchée vers les genoux
                nose_y = 1.0 + np.random.normal(0, 0.1)
            elif label == "Bras vers voisin":
                # Bras tendu vers le voisin
                if np.random.rand() > 0.5:
                    rw_x = 1.6 + np.random.normal(0, 0.1)
                else:
                    lw_x = -1.6 + np.random.normal(0, 0.1)

            # Affecter nez
            feats[0] = nose_x
            feats[1] = nose_y
            # Affecter poignets
            feats[15 * 2] = lw_x
            feats[15 * 2 + 1] = lw_y
            feats[16 * 2] = rw_x
            feats[16 * 2 + 1] = rw_y

            # Bruit léger sur les autres points
            for pt_idx in range(33):
                if pt_idx not in (0, 11, 12, 15, 16, 23, 24, 25, 26):
                    feats[pt_idx * 2] = np.random.normal(0, 0.2)
                    feats[pt_idx * 2 + 1] = np.random.normal(0, 0.2)

            X_list.append(feats)
            y_list.append(label)

    return np.array(X_list), np.array(y_list)


def train():
    os.makedirs(OUTPUT_MODEL_DIR, exist_ok=True)

    if os.path.exists(DATASET_CSV):
        print(f"[Train] Chargement des données réelles depuis : {DATASET_CSV}")
        X_list, y_list = [], []
        with open(DATASET_CSV, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                if not row or len(row) < 67:
                    continue
                # Exclure toute ancienne mention de téléphone par sécurité
                lbl = row[-1].strip()
                if "telephone" in lbl.lower():
                    continue
                feats = [float(v) for v in row[:-1]]
                X_list.append(feats)
                y_list.append(lbl)

        if len(X_list) >= 20:
            X = np.array(X_list, dtype=np.float32)
            y = np.array(y_list)
        else:
            print("[Train] CSV avec trop peu d'échantillons (<20). Utilisation du générateur de base.")
            X, y = generate_baseline_dataset()
    else:
        print(f"[Train] Fichier {DATASET_CSV} introuvable. Entraînement sur données de référence.")
        X, y = generate_baseline_dataset()

    print(f"[Train] Nombre total d'exemples d'apprentissage : {len(X)}")
    print(f"[Train] Classes prises en charge : {sorted(list(set(y)))}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[Train] Précision du modèle sur le test set : {acc * 100:.2f}%")
    print("\n[Train] Rapport de classification :")
    print(classification_report(y_test, y_pred))

    joblib.dump(clf, OUTPUT_MODEL_PATH)
    print(f"[Succès] Modèle IA sauvegardé avec succès dans : {OUTPUT_MODEL_PATH}")


if __name__ == "__main__":
    train()
