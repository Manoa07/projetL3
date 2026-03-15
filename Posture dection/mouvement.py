import math

# --------- OUTILS MATH ---------

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

        angle = calculate_angle(left_ear,nose,right_ear)

        if angle < 140:
            return "Tete tournee"

    return None


# --------- REGARDER VOISIN ---------

def detect_neighbor_cheating(points):

    nose = points[0]
    left_shoulder = points[11]
    right_shoulder = points[12]

    if nose and left_shoulder and right_shoulder:

        center = (left_shoulder[0] + right_shoulder[0]) / 2

        if nose[0] < center - 40:
            return "Regarde voisin gauche"

        if nose[0] > center + 40:
            return "Regarde voisin droite"

    return None


# --------- MAIN SOUS TABLE ---------

def detect_hand_under_table(points):

    left_wrist = points[15]
    right_wrist = points[16]
    left_hip = points[23]
    right_hip = points[24]

    if left_wrist and left_hip:

        if left_wrist[1] > left_hip[1] + 50:
            return "Main gauche sous table"

    if right_wrist and right_hip:

        if right_wrist[1] > right_hip[1] + 50:
            return "Main droite sous table"

    return None


# --------- TELEPHONE ---------

def detect_phone(points):

    nose = points[0]
    left_wrist = points[15]
    right_wrist = points[16]

    if nose:

        if left_wrist:

            dist = abs(left_wrist[0]-nose[0]) + abs(left_wrist[1]-nose[1])

            if dist < 120:
                return "Telephone probable"

        if right_wrist:

            dist = abs(right_wrist[0]-nose[0]) + abs(right_wrist[1]-nose[1])

            if dist < 120:
                return "Telephone probable"

    return None


# --------- ANTISECHE JAMBE ---------

def detect_leg_cheat(points):

    nose = points[0]
    left_knee = points[25]
    right_knee = points[26]

    if nose and left_knee:

        if nose[1] > left_knee[1] - 50:
            return "Regarde antisèche jambe"

    if nose and right_knee:

        if nose[1] > right_knee[1] - 50:
            return "Regarde antisèche jambe"

    return None


# --------- AIDER VOISIN ---------

def detect_helping_neighbor(points):

    nose = points[0]
    left_wrist = points[15]
    right_wrist = points[16]

    if nose:

        if left_wrist and left_wrist[0] > nose[0] + 80:
            return "Bras vers voisin"

        if right_wrist and right_wrist[0] < nose[0] - 80:
            return "Bras vers voisin"

    return None


# --------- CHUCHOTEMENT ---------

def detect_whispering(noses):

    alerts = []

    for i in range(len(noses)):
        for j in range(i+1,len(noses)):

            n1 = noses[i]
            n2 = noses[j]

            dist = abs(n1[0]-n2[0]) + abs(n1[1]-n2[1])

            if dist < 150:

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
