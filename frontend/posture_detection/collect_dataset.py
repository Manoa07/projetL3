"""
Script de collecte automatique de données par Webcam guidée (Méthode 1).
Guide l'utilisateur étape par étape avec un compte à rebours visuel à l'écran,
enregistre les images dans chaque classe et sauvegarde directement les landmarks normalisés.
Compatible avec MediaPipe Tasks (PoseLandmarker).
"""

import os
import sys
import time
import csv
import cv2
import mediapipe as mp
import numpy as np

from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode

# Importation de l'extracteur de features normalisé
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    from .classifier import extract_features
except (ImportError, ValueError):
    try:
        from classifier import extract_features
    except ImportError:
        sys.path.append(CURRENT_DIR)
        from classifier import extract_features

DATASET_DIR = os.path.join(CURRENT_DIR, "dataset_postures")
CSV_PATH = os.path.join(DATASET_DIR, "landmarks_dataset.csv")

# Chemin vers le modèle pose_landmarker.task
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
    raise FileNotFoundError("Impossible de trouver le fichier 'pose_landmarker.task'. Vérifiez le dossier models/.")

# Connexions squelette pour le dessin
POSE_CONNECTIONS = [
    (11, 12),
    (11, 13), (13, 15),
    (12, 14), (14, 16),
    (11, 23), (12, 24),
    (23, 24),
    (23, 25), (25, 27), (27, 31),
    (24, 26), (26, 28), (28, 32)
]

# Liste des postures guidées (Dossier, Titre affiché, Instructions)
POSTURES = [
    {
        "folder": "normal",
        "title": "1/5 : Posture Normale",
        "instruction": "Asseyez-vous normalement, regardez droit devant / votre copie.",
        "samples": 60
    },
    {
        "folder": "regarde_voisin_gauche",
        "title": "2/5 : Regarde Voisin Gauche",
        "instruction": "Tournez la tete vers la GAUCHE comme pour tricher.",
        "samples": 60
    },
    {
        "folder": "regarde_voisin_droite",
        "title": "3/5 : Regarde Voisin Droite",
        "instruction": "Tournez la tete vers la DROITE comme pour tricher.",
        "samples": 60
    },
    {
        "folder": "main_sous_table",
        "title": "4/5 : Main Sous la Table",
        "instruction": "Cachez une ou vos deux mains sous la table.",
        "samples": 60
    },
    {
        "folder": "regarde_antiseche",
        "title": "5/5 : Regarde Antiseche / Jambes",
        "instruction": "Baissez la tete vers vos jambes / vers le bas.",
        "samples": 60
    }
]


def draw_skeleton(frame, landmarks, w, h):
    """Dessine les articulations et connexions du squelette sur l'image."""
    pts = {}
    for i, lm in enumerate(landmarks):
        if getattr(lm, "visibility", 1.0) > 0.4:
            x, y = int(lm.x * w), int(lm.y * h)
            pts[i] = (x, y)
            cv2.circle(frame, (x, y), 4, (0, 255, 255), -1)

    for a, b in POSE_CONNECTIONS:
        if a in pts and b in pts:
            cv2.line(frame, pts[a], pts[b], (255, 255, 255), 2)


def draw_overlay(frame, title, subtitle, countdown=None, progress=None, color=(0, 255, 0)):
    """Affiche un bandeau informatif élégant sur l'image pour guider l'utilisateur."""
    h, w, _ = frame.shape

    # Bandeau supérieur semi-transparent
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 110), (25, 25, 25), -1)

    # Bandeau inférieur pour la progression
    cv2.rectangle(overlay, (0, h - 50), (w, h), (25, 25, 25), -1)

    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Titre de la posture
    cv2.putText(frame, title, (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)
    # Instruction
    cv2.putText(frame, subtitle, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 1, cv2.LINE_AA)

    # Compte à rebours géant au centre si actif
    if countdown is not None and countdown > 0:
        center_text = f"Pret dans : {int(countdown) + 1}s"
        text_size = cv2.getTextSize(center_text, cv2.FONT_HERSHEY_DUPLEX, 1.6, 3)[0]
        tx = (w - text_size[0]) // 2
        ty = (h + text_size[1]) // 2

        # Boîte d'accentuation centrale
        cv2.rectangle(frame, (tx - 20, ty - text_size[1] - 20), (tx + text_size[0] + 20, ty + 20), (0, 0, 0), -1)
        cv2.rectangle(frame, (tx - 20, ty - text_size[1] - 20), (tx + text_size[0] + 20, ty + 20), color, 2)
        cv2.putText(frame, center_text, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 1.6, color, 3, cv2.LINE_AA)

    # Barre de progression et touches
    bottom_text = f"Progression : {progress}" if progress else "Appuyez sur [Q] pour quitter"
    cv2.putText(frame, bottom_text, (20, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)


def main():
    print("=" * 65)
    print("  COLLECTEUR GUIDÉ DE POSTURES PAR WEBCAM (MÉTHODE 1)")
    print("=" * 65)
    print("Ce script va enregistrer 5 postures (60 images chacune = 300 exemples).")
    print("Pour chaque posture :")
    print("  1. Compte à rebours de 4 secondes pour vous mettre en position.")
    print("  2. Enregistrement automatique et continu pendant ~3 secondes.")
    print("=" * 65)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERREUR] Impossible d'ouvrir la webcam.")
        return

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO,
        num_poses=1
    )
    landmarker = PoseLandmarker.create_from_options(options)

    # Préparation du CSV
    os.makedirs(DATASET_DIR, exist_ok=True)
    headers = [f"feat_{i}" for i in range(66)] + ["label"]

    write_header = not os.path.exists(CSV_PATH)
    csv_file = open(CSV_PATH, mode="a", newline="", encoding="utf-8")
    writer = csv.writer(csv_file)
    if write_header:
        writer.writerow(headers)

    total_saved_all = 0
    start_session_ms = int(time.time() * 1000)
    last_timestamp_ms = -1

    window_name = "Enregistreur Automatique de Postures (Appuyez sur 'Q' pour quitter)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 900, 600)

    try:
        for idx, posture in enumerate(POSTURES):
            folder_name = posture["folder"]
            title = posture["title"]
            instruction = posture["instruction"]
            target_count = posture["samples"]

            folder_path = os.path.join(DATASET_DIR, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            print(f"\n---> Préparation pour : {title}")
            print(f"     Consigne : {instruction}")

            # PHASE 1 : COMPTE À REBOURS (4 secondes pour s'installer)
            countdown_duration = 4.0
            phase_start = time.time()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)  # Effet miroir naturel
                h, w, _ = frame.shape
                elapsed = time.time() - phase_start
                remaining = countdown_duration - elapsed

                # Inférence MediaPipe pour visualiser le squelette
                ts = int(time.time() * 1000) - start_session_ms + 1
                if ts <= last_timestamp_ms:
                    ts = last_timestamp_ms + 1
                last_timestamp_ms = ts

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                try:
                    res = landmarker.detect_for_video(mp_img, ts)
                    if res and res.pose_landmarks and len(res.pose_landmarks) > 0:
                        draw_skeleton(frame, res.pose_landmarks[0], w, h)
                except Exception:
                    pass

                draw_overlay(frame, title, instruction, countdown=remaining, progress="Mise en place...", color=(0, 165, 255))
                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("[INFO] Arrêt demandé par l'utilisateur.")
                    return

                if remaining <= 0:
                    break

            # PHASE 2 : CAPTURE AUTOMATIQUE DES 60 SAMPLES
            saved_count = 0
            print(f"     [EN COURS] Enregistrement de {target_count} échantillons...")

            while saved_count < target_count:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape

                ts = int(time.time() * 1000) - start_session_ms + 1
                if ts <= last_timestamp_ms:
                    ts = last_timestamp_ms + 1
                last_timestamp_ms = ts

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

                try:
                    res = landmarker.detect_for_video(mp_img, ts)
                except Exception:
                    res = None

                if res and res.pose_landmarks and len(res.pose_landmarks) > 0:
                    landmarks = res.pose_landmarks[0]
                    # Extraction des 66 coordonnées normalisées
                    feats = extract_features(landmarks)

                    # 1. Sauvegarde dans le CSV
                    writer.writerow(list(feats) + [folder_name])
                    csv_file.flush()

                    # 2. Sauvegarde de l'image brute dans le dossier
                    img_filename = f"{folder_name}_{int(time.time() * 1000)}_{saved_count}.jpg"
                    cv2.imwrite(os.path.join(folder_path, img_filename), frame)

                    saved_count += 1
                    total_saved_all += 1

                    # Dessin du squelette
                    draw_skeleton(frame, landmarks, w, h)

                # Overlay avec barre de capture en direct (vert fluo)
                progress_text = f"{saved_count}/{target_count} images enregistrees"
                draw_overlay(frame, title, "ENREGISTREMENT EN COURS - Maintenez la posture", countdown=None, progress=progress_text, color=(0, 255, 0))

                cv2.imshow(window_name, frame)
                key = cv2.waitKey(20) & 0xFF
                if key == ord('q'):
                    print("[INFO] Arrêt demandé par l'utilisateur.")
                    return

            print(f"     [SUCCÈS] {saved_count} images et landmarks sauvegardés pour '{folder_name}'.")
            time.sleep(0.5)

    finally:
        csv_file.close()
        try:
            landmarker.close()
        except Exception:
            pass
        cap.release()
        cv2.destroyAllWindows()

    print("\n" + "=" * 65)
    print(f"  FÉLICITATIONS ! {total_saved_all} ÉCHANTILLONS ENREGISTRÉS AU TOTAL.")
    print("=" * 65)
    print("Vos données sont prêtes. Vous pouvez maintenant lancer l'entraînement :")
    print("  python frontend/posture_detection/train_model.py\n")


if __name__ == "__main__":
    main()
