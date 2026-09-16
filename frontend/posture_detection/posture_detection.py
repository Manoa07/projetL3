import cv2
import mediapipe as mp
import os
import time
import json
import sys
import tempfile
import requests
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker
from mediapipe.tasks.python.vision import PoseLandmarkerOptions
from mediapipe.tasks.python.vision import RunningMode
try:
    from .mouvement import detect_suspicious_movements, detect_whispering
except Exception:
    from mouvement import detect_suspicious_movements, detect_whispering

# Chemin vers le modèle
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "../models/pose_landmarker.task")
_DEBUG_LOG_PATH = os.path.abspath(os.path.join(current_dir, "..", "debug-1f4ecf.log"))
_DEBUG_LOG_PATH_FALLBACK = os.path.join(tempfile.gettempdir(), "debug-1f4ecf.log")

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=RunningMode.VIDEO,
    num_poses=10
)

# Tolérance de visibilité (augmentée pour ignorer les points peu fiables)
define_precision_tolerance = 0.6

# Tracking étudiants
students = {}
student_id_counter = 0

# Compteurs de suspicion par (student_id, type_event)
suspicion_counters = {}
SUSPICION_THRESHOLD = 5   # nombre de frames consécutives nécessaires

# Connexions squelette
POSE_CONNECTIONS = [
    (11,12),
    (11,13),(13,15),
    (12,14),(14,16),
    (11,23),(12,24),
    (23,24),
    (23,25),(25,27),(27,31),
    (24,26),(26,28),(28,32)
]

# --------- Utils ---------
def _debug_log(hypothesis_id, location, message, data=None, run_id="pre-fix"):
    payload = {
        "sessionId": "1f4ecf",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return
    except Exception:
        pass
    try:
        with open(_DEBUG_LOG_PATH_FALLBACK, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return
    except Exception:
        pass
    try:
        print("[debug-log-failed]", payload)
    except Exception:
        pass

print(
    "[agent-debug] module import",
    {
        "file": __file__,
        "cwd": os.getcwd(),
        "py": sys.executable,
        "argv": sys.argv,
        "debug_log_path": _DEBUG_LOG_PATH,
        "debug_log_path_fallback": _DEBUG_LOG_PATH_FALLBACK,
    },
    flush=True,
)
_debug_log(
    "H1",
    "posture_detection.py:module:paths",
    "Module loaded / paths resolved",
    {
        "cwd": os.getcwd(),
        "file": __file__,
        "model_path": model_path,
        "model_exists": os.path.exists(model_path),
        "debug_log_path": _DEBUG_LOG_PATH,
    },
)

# BUG-02 : L'instance PoseLandmarker est créée dans VideoThread.run() et dans main().
# On ne crée plus d'instance globale ici pour éviter le double chargement en mémoire.
# La fonction main() crée sa propre instance locale.

def _l1_dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def _l2_dist(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


last_sent = {}

# WARN-03 : id_examen courant, mis à jour par l'interface avant le lancement
current_examen_id: int = 1


def set_current_examen(id_examen: int):
    """Appelé par l'interface pour définir l'examen en cours de surveillance."""
    global current_examen_id
    current_examen_id = id_examen


def send_alert_to_api(id_eleve, remarque):
    key = f"{id_eleve}-{remarque}"
    now = time.time()
    if key in last_sent and now - last_sent[key] < 5:
        return
    last_sent[key] = now
    try:
        data = {
            "id_examen":    current_examen_id,   # WARN-03 : valeur dynamique
            "id_eleve":     id_eleve,
            "Status_examen": "suspect",
            "Remarque":     remarque,
        }
        requests.post(
            "http://127.0.0.1:8000/surveillance/create",
            json=data,
            timeout=2,
        )
    except Exception as e:
        print("Erreur API :", e)

def main():
    global student_id_counter

    _debug_log(
        "H1",
        "posture_detection.py:main:start",
        "Starting main",
        {
            "cwd": os.getcwd(),
            "file": __file__,
            "model_path": model_path,
            "model_exists": os.path.exists(model_path),
            "running_mode": str(options.running_mode),
        },
    )

    # BUG-02 : instance locale à main(), indépendante de VideoThread
    pose_landmarker = PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 30.0
    frame_idx = 0
    # BUG-03 : timestamp relatif au démarrage (MediaPipe VIDEO exige croissance depuis 0)
    start_ms = int(time.time() * 1000)
    last_timestamp_ms = -1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            _debug_log("H2", "posture_detection.py:main:cap_read", "Camera read failed", {"ret": ret})
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        computed_ms = int((frame_idx * 1000.0) / fps)
        wall_ms = int(time.time() * 1000) - start_ms
        timestamp_ms = computed_ms if computed_ms > 0 else wall_ms
        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1
        last_timestamp_ms = timestamp_ms
        frame_idx += 1

        try:
            result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)
        except Exception as e:
            _debug_log(
                "H3",
                "posture_detection.py:main:detect_for_video:exception",
                "detect_for_video raised",
                {"type": type(e).__name__, "error": str(e)},
            )
            raise

        # Pour les alertes globales (chuchotement) on les traite séparément plus tard
        all_global_alerts = []

        if result.pose_landmarks:
            noses = []
            # Premier passage pour attribuer les ID et stocker les points
            for landmarks in result.pose_landmarks:
                points = [None] * len(landmarks)
                for i, lm in enumerate(landmarks):
                    if lm.visibility > define_precision_tolerance:
                        x = int(lm.x * w)
                        y = int(lm.y * h)
                        points[i] = (x, y)
                        cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

                # Dessin squelette
                for a, b in POSE_CONNECTIONS:
                    p1 = points[a]
                    p2 = points[b]
                    if p1 and p2:
                        cv2.line(frame, p1, p2, (255, 255, 255), 2)

                # Articulations principales
                p11 = points[11]
                if p11:
                    cv2.circle(frame, p11, 8, (255, 0, 0), -1)
                p12 = points[12]
                if p12:
                    cv2.circle(frame, p12, 8, (255, 0, 0), -1)

                # Tracking étudiant
                nose = points[0]
                if nose:
                    noses.append(nose)

                    assigned_id = None
                    best_dist = None
                    for sid, pos in students.items():
                        dist = _l1_dist(pos, nose)
                        if dist < 80 and (best_dist is None or dist < best_dist):
                            assigned_id = sid
                            best_dist = dist

                    if assigned_id is None:
                        student_id_counter += 1
                        assigned_id = student_id_counter

                    students[assigned_id] = nose

                    # Analyse comportementale pour cet étudiant via le classifieur IA
                    events = detect_suspicious_movements(points)

                    # Mise à jour des compteurs pour cet étudiant
                    # On considère que s'il n'y a pas d'événement, on efface ses compteurs
                    # (ou on les décrémente ? Ici on efface totalement pour éviter les alertes persistantes)
                    if events:
                        for e in events:
                            key = (assigned_id, e)
                            suspicion_counters[key] = suspicion_counters.get(key, 0) + 1
                            if suspicion_counters[key] >= SUSPICION_THRESHOLD:
                                send_alert_to_api(assigned_id, e)
                                # Réinitialiser pour ne pas renvoyer immédiatement
                                suspicion_counters[key] = 0
                    else:
                        # Pas d'événement : on réinitialise tous les compteurs de cet étudiant
                        keys_to_remove = [k for k in suspicion_counters if k[0] == assigned_id]
                        for k in keys_to_remove:
                            del suspicion_counters[k]

                    # Affichage des événements sur l'image (optionnel)
                    y = nose[1] + 20
                    for e in events:
                        cv2.putText(
                            frame,
                            e,
                            (nose[0], y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2,
                        )
                        y += 20

                # On peut aussi ajouter les alertes du module mouvement (désactivées ici pour éviter doublons)
                # mais on conserve pour les alertes globales
                # suspicious_movements = detect_suspicious_movements(points)  # désactivé
                # all_global_alerts.extend(suspicious_movements)

            # Détection chuchotement (global)
            whisper_alerts = detect_whispering(noses)
            if whisper_alerts:
                all_global_alerts.extend(whisper_alerts)

        # Affichage des alertes globales (chuchotement)
        if all_global_alerts:
            cv2.putText(
                frame,
                "Postures suspectes detectees!",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            y_offset = 160
            for movement in all_global_alerts:
                cv2.putText(
                    frame,
                    f"- {movement}",
                    (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )
                y_offset += 30
                # Optionnel : envoyer alerte globale ? On peut envoyer pour chaque étudiant, mais c'est complexe.
                # Ici on choisit de ne pas envoyer d'alerte API pour les alertes globales.

        cv2.imshow("SmartEdu", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("f"):
            cv2.setWindowProperty("SmartEdu", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        elif key == ord("n"):
            cv2.setWindowProperty("SmartEdu", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        elif key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()