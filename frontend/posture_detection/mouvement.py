import os
import sys

# Importation du classifieur IA
try:
    from .classifier import get_classifier
except ImportError:
    from classifier import get_classifier

# --------- SCORE DE SUSPICION (Téléphone totalement supprimé) ---------
SUSPICION_WEIGHTS = {
    # Noms formatés ou anciens
    "Tete tournee": 2,
    "Regarde voisin gauche": 4,
    "Regarde voisin droite": 4,
    "Main sous table": 3,
    "Regarde antiseche jambe": 5,
    "Possible chuchotement": 5,
    # Labels directs issus des classes du modèle entraîné
    "regarde_voisin_gauche": 4,
    "regarde_voisin_droite": 4,
    "main_sous_table": 3,
    "regarde_antiseche": 5,
    "bras_vers_voisin": 4,
}


def compute_suspicion_score(events):
    """
    Calcule le score de suspicion basé sur les événements détectés par l'IA.
    (Note : le téléphone a été retiré des critères de détection).
    """
    score = 0
    for e in events:
        if e in SUSPICION_WEIGHTS:
            score += SUSPICION_WEIGHTS[e]
        elif e != "normal":
            score += 3
    return score


def detect_whispering(noses):
    """
    Détecte si deux étudiants sont anormalement proches (chuchotement possible).
    """
    alerts = []
    if not noses or len(noses) < 2:
        return alerts

    for i in range(len(noses)):
        for j in range(i + 1, len(noses)):
            n1 = noses[i]
            n2 = noses[j]
            if n1 and n2:
                dx = abs(n1[0] - n2[0])
                dy = abs(n1[1] - n2[1])
                if dx < 180 and dy < 90:
                    alerts.append("Possible chuchotement")
    return alerts


def detect_suspicious_movements(points):
    """
    Détection de mouvements / postures suspectes via l'IA (Machine Learning).
    Remplace intégralement les calculs trigonométriques et seuils manuels.
    Le téléphone a été supprimé.
    
    Retourne la liste des événements suspects détectés, ou [] si la posture est normale.
    """
    if not points:
        return []

    classifier = get_classifier()
    label, confidence = classifier.predict(points, min_confidence=0.60)

    # Ignorer posture normale ou confiance trop basse
    if label == "normal" or not label:
        return []

    # Sécurité supplémentaire : s'assurer qu'aucune mention de téléphone n'est émise
    if "telephone" in label.lower():
        return []

    # Formatage lisible des alertes pour l'interface
    label_pretty = {
        "regarde_voisin_gauche": "Regarde voisin gauche",
        "regarde_voisin_droite": "Regarde voisin droite",
        "main_sous_table": "Main sous la table",
        "regarde_antiseche": "Regarde antiseche / jambes",
        "bras_vers_voisin": "Bras vers voisin",
    }.get(label, label)

    return [label_pretty]