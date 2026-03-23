import math
import numpy as np  # utilisé pour l'estimation d'échelle, mais peut être évité

# --------- OUTILS ---------
def _l2_dist(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx*dx + dy*dy)**0.5

def _estimate_person_scale(points):
    """
    Estime la taille apparente de la personne (largeur d'épaules en pixels).
    Retourne None si insuffisant.
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
    Retourne un seuil adapté à l'échelle de la personne.
    """
    if scale is None:
        return float(fallback_px)
    return max(10.0, float(scale) * float(factor))

# --------- ANGLE (pour tête tournée) ---------
def calculate_angle(a,b,c):
    ax,ay = a
    bx,by = b
    cx,cy = c
    angle = math.degrees(
        math.atan2(cy-by,cx-bx) -
        math.atan2(ay-by,ax-bx)
    )
    return abs(angle)

# --------- DETECTION TETE TOURNEE ---------
def detect_head_turn(points):
    nose = points[0]
    left_ear = points[7]
    right_ear = points[8]
    if nose and left_ear and right_ear:
        angle = calculate_angle(left_ear, nose, right_ear)
        # Seuil plus strict : < 130 au lieu de 140
        if angle < 130:
            return "Tete tournee"
    return None

# --------- REGARDER VOISIN ---------
def detect_neighbor_cheating(points):
    nose = points[0]
    left_shoulder = points[11]
    right_shoulder = points[12]
    if nose and left_shoulder and right_shoulder:
        center = (left_shoulder[0] + right_shoulder[0]) / 2
        # Seuil augmenté à 80 pixels (ou adaptatif)
        thr = _scaled_threshold(_estimate_person_scale(points), 80, 0.7)
        if nose[0] < center - thr:
            return "Regarde voisin gauche"
        if nose[0] > center + thr:
            return "Regarde voisin droite"
    return None

# --------- MAIN SOUS TABLE ---------
def detect_hand_under_table(points):
    left_wrist = points[15]
    right_wrist = points[16]
    left_hip = points[23]
    right_hip = points[24]
    scale = _estimate_person_scale(points)
    thr = _scaled_threshold(scale, 80, 0.65)  # fallback 80px, facteur 0.65
    if left_wrist and left_hip and left_wrist[1] > left_hip[1] + thr:
        return "Main gauche sous table"
    if right_wrist and right_hip and right_wrist[1] > right_hip[1] + thr:
        return "Main droite sous table"
    return None

# --------- TELEPHONE ---------
def detect_phone(points):
    nose = points[0]
    left_wrist = points[15]
    right_wrist = points[16]
    if nose:
        scale = _estimate_person_scale(points)
        thr_x = _scaled_threshold(scale, 70, 0.6)   # fallback 70, facteur 0.6
        thr_y = _scaled_threshold(scale, 100, 0.8)  # fallback 100, facteur 0.8
        if left_wrist and abs(left_wrist[0]-nose[0]) < thr_x and abs(left_wrist[1]-nose[1]) < thr_y:
            return "Telephone probable"
        if right_wrist and abs(right_wrist[0]-nose[0]) < thr_x and abs(right_wrist[1]-nose[1]) < thr_y:
            return "Telephone probable"
    return None

# --------- ANTISECHE JAMBE ---------
def detect_leg_cheat(points):
    nose = points[0]
    left_knee = points[25]
    right_knee = points[26]
    scale = _estimate_person_scale(points)
    thr = _scaled_threshold(scale, 70, 0.65)
    if nose and left_knee:
        if nose[1] > left_knee[1] - thr:
            return "Regarde antisèche jambe"
    if nose and right_knee:
        if nose[1] > right_knee[1] - thr:
            return "Regarde antisèche jambe"
    return None

# --------- AIDER VOISIN ---------
def detect_helping_neighbor(points):
    nose = points[0]
    left_wrist = points[15]
    right_wrist = points[16]
    scale = _estimate_person_scale(points)
    thr = _scaled_threshold(scale, 120, 1.0)  # seuil plus grand pour les bras tendus
    if nose:
        if left_wrist and left_wrist[0] > nose[0] + thr:
            return "Bras vers voisin"
        if right_wrist and right_wrist[0] < nose[0] - thr:
            return "Bras vers voisin"
    return None

# --------- CHUCHOTEMENT ---------
def detect_whispering(noses):
    """
    Détecte deux personnes proches. Utilise maintenant une distance verticale aussi.
    """
    alerts = []
    for i in range(len(noses)):
        for j in range(i+1, len(noses)):
            n1 = noses[i]
            n2 = noses[j]
            # distance horizontale
            dx = abs(n1[0] - n2[0])
            dy = abs(n1[1] - n2[1])
            # On estime l'échelle approximative (moyenne des épaules si possible, mais ici on utilise une valeur fixe)
            # Pour rendre adaptatif, on pourrait passer un scale moyen, mais on utilise des seuils fixes pour simplifier.
            # Seuil horizontal : 200 px (ancien 150) ; vertical : 100 px
            if dx < 200 and dy < 100:
                alerts.append("Possible chuchotement")
    return alerts

# --------- SCORE SUSPICION ---------
def compute_suspicion_score(events):
    weights = {
        "Telephone probable":6,
        "Tete tournee":2,
        "Regarde voisin gauche":4,
        "Regarde voisin droite":4,
        "Main gauche sous table":3,
        "Main droite sous table":3,
        "Regarde antisèche jambe":5,
        "Bras vers voisin":4,
        "Possible chuchotement":5
    }
    score = 0
    for e in events:
        if e in weights:
            score += weights[e]
    return score

# --------- FONCTION PRINCIPALE ---------
def detect_suspicious_movements(points):
    events = []
    for func in [
        detect_head_turn,
        detect_neighbor_cheating,
        detect_hand_under_table,
        detect_phone,
        detect_leg_cheat,
        detect_helping_neighbor
    ]:
        e = func(points)
        if e:
            events.append(e)
    return events