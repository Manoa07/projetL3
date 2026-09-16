"""
Script pour extraire les caractéristiques des squelettes (landmarks)
à partir d'images de postures et générer un fichier CSV prêt pour l'entraînement.
Compatible avec MediaPipe Tasks (PoseLandmarker en mode IMAGE).
"""

import os
import sys
import cv2
import csv
import mediapipe as mp
import numpy as np

from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    from .classifier import extract_features
except (ImportError, ValueError):
    try:
        from classifier import extract_features
    except ImportError:
        sys.path.append(CURRENT_DIR)
        from classifier import extract_features

DEFAULT_DATASET_DIR = os.path.join(CURRENT_DIR, "dataset_postures")
DEFAULT_CSV_PATH = os.path.join(DEFAULT_DATASET_DIR, "landmarks_dataset.csv")

# Chemin du modèle pose_landmarker.task
POSSIBLE_TASK_PATHS = [
    os.path.join(CURRENT_DIR, "../models/pose_landmarker.task"),
    os.path.join(CURRENT_DIR, "../../models/pose_landmarker.task"),
    os.path.join(os.getcwd(), "models/pose_landmarker.task"),
    os.path.join(os.getcwd(), "frontend/models/pose_landmarker.task"),
]

MODEL_PATH = None
for p in POSSIBLE_TASK_PATHS:
    if os.path.exists(p):
        MODEL_PATH = os.path.abspath(p)
        break

if not MODEL_PATH:
    raise FileNotFoundError("Fichier 'pose_landmarker.task' introuvable.")


def extract_landmarks_from_images(dataset_dir=DEFAULT_DATASET_DIR, output_csv=DEFAULT_CSV_PATH):
    """
    Parcourt les sous-dossiers de dataset_dir (chaque sous-dossier = nom d'une posture)
    et extrait les 66 features normalisées pour chaque image.
    """
    if not os.path.exists(dataset_dir):
        print(f"[Erreur] Le dossier {dataset_dir} n'existe pas.")
        return False

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.IMAGE,
        num_poses=1
    )
    landmarker = PoseLandmarker.create_from_options(options)

    headers = [f"feat_{i}" for i in range(66)] + ["label"]
    rows_written = 0

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        classes = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
        print(f"[Info] Classes détectées : {classes}")

        for label in classes:
            class_folder = os.path.join(dataset_dir, label)
            valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
            image_files = [f for f in os.listdir(class_folder) if f.lower().endswith(valid_extensions)]

            print(f" -> Traitement de la classe '{label}' ({len(image_files)} images)...")

            for img_name in image_files:
                img_path = os.path.join(class_folder, img_name)
                image = cv2.imread(img_path)
                if image is None:
                    continue

                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

                try:
                    res = landmarker.detect(mp_img)
                    if res and res.pose_landmarks and len(res.pose_landmarks) > 0:
                        landmarks = res.pose_landmarks[0]
                        feats = extract_features(landmarks)
                        row = list(feats) + [label]
                        writer.writerow(row)
                        rows_written += 1
                except Exception as e:
                    pass

    try:
        landmarker.close()
    except Exception:
        pass

    print(f"[Succès] {rows_written} exemples extraits et enregistrés dans : {output_csv}")
    return True


if __name__ == "__main__":
    extract_landmarks_from_images()
