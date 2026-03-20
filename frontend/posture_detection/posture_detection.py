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
    # When `posture_detection` is a package (recommended).
    from .mouvement import detect_suspicious_movements, detect_whispering
except Exception:
    # When run as a standalone script from the repo root or another cwd.
    from mouvement import detect_suspicious_movements, detect_whispering

# Chemin vers le modèle
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "../models/pose_landmarker.task")  # Ajuste selon ta structure
_DEBUG_LOG_PATH = os.path.abspath(os.path.join(current_dir, "..", "debug-1f4ecf.log"))
_DEBUG_LOG_PATH_FALLBACK = os.path.join(tempfile.gettempdir(), "debug-1f4ecf.log")

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    # VIDEO mode enables temporal tracking inside MediaPipe (faster and more stable than IMAGE per frame).
    running_mode=RunningMode.VIDEO,
    num_poses=10
)

# Tolérance de visibilité
define_precision_tolerance = 0.5

# Tracking étudiants (stocke position uniquement)
students = {}
student_id_counter = 0

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

# --------- Utils (lightweight, no extra deps) ---------
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
        # Last-resort visibility if file writes fail.
        print("[debug-log-failed]", payload)
    except Exception:
        pass


# #region agent log
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
# #endregion agent log

try:
    # #region agent log
    _debug_log(
        "H1",
        "posture_detection.py:module:pose_init",
        "Creating PoseLandmarker",
        {"running_mode": str(options.running_mode)},
    )
    # #endregion agent log
    pose_landmarker = PoseLandmarker.create_from_options(options)
except Exception as e:
    # #region agent log
    _debug_log(
        "H1",
        "posture_detection.py:module:pose_init:exception",
        "PoseLandmarker init failed",
        {"type": type(e).__name__, "error": str(e)},
    )
    # #endregion agent log
    raise


def _l1_dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _l2_dist(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


def _estimate_person_scale(points):
    """
    Returns an approximate pixel scale for the person (shoulder width preferred),
    falling back to hip width, then torso length. If insufficient landmarks, returns None.
    """
    left_shoulder = points[11]
    right_shoulder = points[12]
    if left_shoulder and right_shoulder:
        s = _l2_dist(left_shoulder, right_shoulder)
        if s > 1:
            return s

    left_hip = points[23]
    right_hip = points[24]
    if left_hip and right_hip:
        s = _l2_dist(left_hip, right_hip)
        if s > 1:
            return s

    if left_shoulder and left_hip:
        s = _l2_dist(left_shoulder, left_hip)
        if s > 1:
            return s
    if right_shoulder and right_hip:
        s = _l2_dist(right_shoulder, right_hip)
        if s > 1:
            return s

    return None


def _scaled_threshold(scale, fallback_px, factor):
    """
    Scale a pixel threshold with the person's apparent size.
    If scale is unavailable, fall back to the original hardcoded pixel threshold.
    """
    if scale is None:
        return float(fallback_px)
    return max(10.0, float(scale) * float(factor))


# Détection tête tournée
def detect_head_turn(points):
    nose = points[0]
    left_ear = points[7]
    right_ear = points[8]
    if nose and left_ear and right_ear:
        center = (left_ear[0] + right_ear[0]) / 2
        scale = _estimate_person_scale(points)
        # Original threshold: 40px. Now scale-aware for consistent behavior across resolutions/distances.
        thr = _scaled_threshold(scale, fallback_px=40, factor=0.33)
        if abs(nose[0] - center) > thr:
            return "Tete tourne" 
    return None

# Détection main sous table
def detect_hand_under_table(points):
    left_wrist = points[15]
    right_wrist = points[16]
    left_hip = points[23]
    right_hip = points[24]
    scale = _estimate_person_scale(points)
    # Original threshold: 50px below hip. Use scale-aware vertical margin.
    thr = _scaled_threshold(scale, fallback_px=50, factor=0.40)
    if left_wrist and left_hip and left_wrist[1] > left_hip[1] + thr:
        return "Main gauche sous table"
    if right_wrist and right_hip and right_wrist[1] > right_hip[1] + thr:
        return "Main droite sous table"
    return None

# Détection téléphone
def detect_phone(points):
    nose = points[0]
    left_wrist = points[15]
    right_wrist = points[16]
    if nose:
        scale = _estimate_person_scale(points)
        thr_x = _scaled_threshold(scale, fallback_px=50, factor=0.42)
        thr_y = _scaled_threshold(scale, fallback_px=80, factor=0.65)
        if left_wrist and abs(left_wrist[0]-nose[0]) < thr_x and abs(left_wrist[1]-nose[1]) < thr_y:
            return "Telephone suspect"
        if right_wrist and abs(right_wrist[0]-nose[0]) < thr_x and abs(right_wrist[1]-nose[1]) < thr_y:
            return "Telephone suspect"
    return None

last_sent = {}  

def send_alert_to_api(id_eleve, remarque):
    key = f"{id_eleve}-{remarque}"
    now = time.time()

    # Anti-spam (5 secondes)
    if key in last_sent and now - last_sent[key] < 5:
        return

    last_sent[key] = now

    try:
        data = {
            "id_examen": 1,
            "id_eleve": id_eleve,
            "Status_examen": "suspect",
            "Remarque": remarque
        }

        requests.post(
            "http://127.0.0.1:8000/surveillance/create",
            json=data,
            timeout=2
        )
    except Exception as e:
        print("Erreur API :", e)

def main():
    global student_id_counter

    # Capture webcam
    # #region agent log
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
    # #endregion agent log

    cap = cv2.VideoCapture(0)
    # Reduce internal buffering to lower latency (best-effort; may be ignored by some backends).
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 30.0
    frame_idx = 0
    start_time = time.time()
    last_timestamp_ms = -1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            # #region agent log
            _debug_log("H2", "posture_detection.py:main:cap_read", "Camera read failed", {"ret": ret})
            # #endregion agent log
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # VIDEO mode requires strictly increasing timestamps.
        # Some backends report odd/high FPS values which can cause int-truncation duplicates.
        computed_ms = int((frame_idx * 1000.0) / fps)
        wall_ms = int((time.time() - start_time) * 1000.0)
        timestamp_ms = computed_ms if computed_ms > 0 else wall_ms
        if timestamp_ms <= last_timestamp_ms:
            timestamp_ms = last_timestamp_ms + 1
        last_timestamp_ms = timestamp_ms
        frame_idx += 1

        try:
            # #region agent log
            _debug_log(
                "H3",
                "posture_detection.py:main:detect_for_video",
                "Calling detect_for_video",
                {
                    "timestamp_ms": timestamp_ms,
                    "computed_ms": computed_ms,
                    "wall_ms": wall_ms,
                    "last_timestamp_ms": last_timestamp_ms,
                    "fps": fps,
                    "frame_w": w,
                    "frame_h": h,
                },
            )
            # #endregion agent log
            result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)
        except Exception as e:
            # #region agent log
            _debug_log(
                "H3",
                "posture_detection.py:main:detect_for_video:exception",
                "detect_for_video raised",
                {"type": type(e).__name__, "error": str(e)},
            )
            # #endregion agent log
            raise
        suspicious_movements = []

        if result.pose_landmarks:
            noses = []

            for landmarks in result.pose_landmarks:
                points = [None] * len(landmarks)

                # Convert landmarks once (avoid per-point list growth).
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

                # Analyse comportement
                events = []

                head = detect_head_turn(points)
                if head:
                    events.append(head)

                hand = detect_hand_under_table(points)
                if hand:
                    events.append(hand)

                phone = detect_phone(points)
                if phone:
                    events.append(phone)

                # Tracking étudiant
                nose = points[0]
                if nose:
                    noses.append(nose)

                    assigned_id = None
                    best_dist = None

                    # Parcours des étudiants connus
                    for sid, pos in students.items():
                        dist = _l1_dist(pos, nose)
                        if dist < 80 and (best_dist is None or dist < best_dist):
                            assigned_id = sid
                            best_dist = dist

                    if assigned_id is None:
                        student_id_counter += 1
                        assigned_id = student_id_counter

                    students[assigned_id] = nose

                    # # Affichage étudiant
                    # cv2.putText(
                    #     frame,
                    #     f"Etudiant {assigned_id}",
                    #     (nose[0], nose[1] - 40),
                    #     cv2.FONT_HERSHEY_SIMPLEX,
                    #     0.7,
                    #     (255, 255, 255),
                    #     2,
                    # )

                    # Affichage événements (sans score)
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
                        send_alert_to_api(assigned_id,e)
                        y += 20

                # Détection mouvements suspects déjà existante
                suspicious_movements.extend(detect_suspicious_movements(points))

            # Détection événements multi-personnes (chuchotement)
            whisper_alerts = detect_whispering(noses)
            if whisper_alerts:
                suspicious_movements.extend(whisper_alerts)

        # Affichage alertes
        if suspicious_movements:
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
            for movement in suspicious_movements:
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
