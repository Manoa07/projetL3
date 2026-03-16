import cv2
import mediapipe as mp
import os
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker
from mediapipe.tasks.python.vision import PoseLandmarkerOptions
from mediapipe.tasks.python.vision import RunningMode
from mouvement import detect_suspicious_movements, detect_whispering

# Chemin vers le modèle
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "../models/pose_landmarker.task")  # Ajuste selon ta structure

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=RunningMode.IMAGE,
    num_poses=5
)

pose_landmarker = PoseLandmarker.create_from_options(options)

# Tolérance de visibilité
define_precision_tolerance = 0.6

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

# Détection tête tournée
def detect_head_turn(points):
    nose = points[0]
    left_ear = points[7]
    right_ear = points[8]
    if nose and left_ear and right_ear:
        center = (left_ear[0] + right_ear[0]) / 2
        if abs(nose[0] - center) > 40:
            return "Tete tournee"
    return None

# Détection main sous table
def detect_hand_under_table(points):
    left_wrist = points[15]
    right_wrist = points[16]
    left_hip = points[23]
    right_hip = points[24]
    if left_wrist and left_hip and left_wrist[1] > left_hip[1] + 50:
        return "Main gauche sous table"
    if right_wrist and right_hip and right_wrist[1] > right_hip[1] + 50:
        return "Main droite sous table"
    return None

# Détection téléphone
def detect_phone(points):
    nose = points[0]
    left_wrist = points[15]
    right_wrist = points[16]
    if nose:
        if left_wrist and abs(left_wrist[0]-nose[0]) < 50 and abs(left_wrist[1]-nose[1]) < 80:
            return "Telephone suspect"
        if right_wrist and abs(right_wrist[0]-nose[0]) < 50 and abs(right_wrist[1]-nose[1]) < 80:
            return "Telephone suspect"
    return None

# Capture webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = pose_landmarker.detect(mp_image)
    suspicious_movements = []

    if result.pose_landmarks:
        noses = []

        for landmarks in result.pose_landmarks:
            points = []

            for lm in landmarks:
                if lm.visibility > define_precision_tolerance:
                    x = int(lm.x * w)
                    y = int(lm.y * h)
                    points.append((x, y))
                    cv2.circle(frame, (x, y), 3, (0,255,255), -1)
                else:
                    points.append(None)

            # Dessin squelette
            for connection in POSE_CONNECTIONS:
                p1 = points[connection[0]]
                p2 = points[connection[1]]
                if p1 and p2:
                    cv2.line(frame, p1, p2, (255,255,255), 2)

            # Articulations principales
            if points[11]:
                cv2.circle(frame, points[11], 8, (255,0,0), -1)
            if points[12]:
                cv2.circle(frame, points[12], 8, (255,0,0), -1)

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

            # Note: score removed — only events are used

            # Tracking étudiant
            nose = points[0]

            if nose:
                noses.append(nose)

                assigned_id = None

                # Parcours des étudiants connus
                for sid, pos in students.items():

                    dist = abs(pos[0]-nose[0]) + abs(pos[1]-nose[1])

                    if dist < 80:
                        assigned_id = sid
                        students[sid] = nose
                        break

                if assigned_id is None:

                    student_id_counter += 1
                    students[student_id_counter] = nose
                    assigned_id = student_id_counter

                # Affichage étudiant
                cv2.putText(
                frame,
                f"Etudiant {assigned_id}",
                (nose[0],nose[1]-40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,255),
                2
                )

                # Affichage événements (sans score)
                y = nose[1] + 20

                for e in events:

                    cv2.putText(
                    frame,
                    e,
                    (nose[0],y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,0,255),
                    2
                    )

                    y += 20

            # Détection mouvements suspects déjà existante
            suspicious_movements.extend(detect_suspicious_movements(points))

        # Détection événements multi-personnes (chuchotement)
        whisper_alerts = detect_whispering(noses)
        if whisper_alerts:
            suspicious_movements.extend(whisper_alerts)

    # Affichage alertes
    if suspicious_movements:
        cv2.putText(frame, "Postures suspectes detectees!", (20,120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        y_offset = 160
        for movement in suspicious_movements:
            cv2.putText(frame, f"- {movement}", (20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
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
