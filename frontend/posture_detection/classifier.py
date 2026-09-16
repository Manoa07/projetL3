import os
import math
import joblib
import numpy as np

# Chemins possibles vers le modèle de classification
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_MODEL_PATHS = [
    os.path.join(CURRENT_DIR, "../../models/posture_classifier.pkl"),
    os.path.join(CURRENT_DIR, "../models/posture_classifier.pkl"),
    os.path.join(CURRENT_DIR, "models/posture_classifier.pkl"),
    os.path.join(os.getcwd(), "models/posture_classifier.pkl"),
]


def _extract_coord(pt):
    """
    Extrait (x, y, z) que ce soit un Landmark MediaPipe ou une liste/tuple (x, y[, z]).
    """
    if pt is None:
        return None
    if hasattr(pt, "x") and hasattr(pt, "y"):
        z = getattr(pt, "z", 0.0)
        return float(pt.x), float(pt.y), float(z)
    if isinstance(pt, (list, tuple)):
        if len(pt) >= 3:
            return float(pt[0]), float(pt[1]), float(pt[2])
        if len(pt) >= 2:
            return float(pt[0]), float(pt[1]), 0.0
    return None


def extract_features(points_or_landmarks):
    """
    Transforme les 33 points squelettes en un vecteur de caractéristiques
    normalisé, centré et indépendant de la distance caméra / échelle.
    Taille du vecteur : 66 (33 points x 2 coordonnées x, y)
    """
    if not points_or_landmarks:
        return np.zeros(66, dtype=np.float32)

    raw_points = [_extract_coord(pt) for pt in points_or_landmarks]
    # S'assurer qu'on a au moins 33 points
    while len(raw_points) < 33:
        raw_points.append(None)

    # 1. Calcul du point central (centre des épaules ou des hanches)
    p_ls = raw_points[11]  # Épaule gauche
    p_rs = raw_points[12]  # Épaule droite
    p_lh = raw_points[23]  # Hanche gauche
    p_rh = raw_points[24]  # Hanche droite

    if p_ls and p_rs:
        center_x = (p_ls[0] + p_rs[0]) / 2.0
        center_y = (p_ls[1] + p_rs[1]) / 2.0
    elif p_lh and p_rh:
        center_x = (p_lh[0] + p_rh[0]) / 2.0
        center_y = (p_lh[1] + p_rh[1]) / 2.0
    elif raw_points[0]:  # Nez
        center_x = raw_points[0][0]
        center_y = raw_points[0][1]
    else:
        center_x, center_y = 0.0, 0.0

    # 2. Facteur d'échelle (distance inter-épaules ou épaules-hanches)
    scale = 1.0
    if p_ls and p_rs:
        d = math.hypot(p_ls[0] - p_rs[0], p_ls[1] - p_rs[1])
        if d > 1e-3:
            scale = d
    elif p_lh and p_rh:
        d = math.hypot(p_lh[0] - p_rh[0], p_lh[1] - p_rh[1])
        if d > 1e-3:
            scale = d

    # 3. Construction du vecteur de 66 features (x_norm, y_norm)
    features = []
    for i in range(33):
        pt = raw_points[i]
        if pt is None:
            features.extend([0.0, 0.0])
        else:
            norm_x = (pt[0] - center_x) / scale
            norm_y = (pt[1] - center_y) / scale
            features.extend([norm_x, norm_y])

    return np.array(features, dtype=np.float32)


class PostureClassifier:
    """
    Classifieur IA de postures suspectes pour la surveillance d'examen.
    Remplace les calculs mathématiques manuels par un modèle Machine Learning entraîné.
    Note : Le téléphone a été complètement retiré du système de détection.
    """

    def __init__(self, model_path=None):
        self.model = None
        self.model_path = None
        self.load_model(model_path)

    def load_model(self, model_path=None):
        targets = [model_path] if model_path else POSSIBLE_MODEL_PATHS
        for path in targets:
            if path and os.path.exists(path):
                try:
                    self.model = joblib.load(path)
                    self.model_path = path
                    print(f"[PostureClassifier] Modèle IA chargé avec succès depuis: {path}")
                    return True
                except Exception as e:
                    print(f"[PostureClassifier] Erreur chargement modèle ({path}): {e}")
        return False

    def predict(self, points_or_landmarks, min_confidence=0.65):
        """
        Prédit la posture à partir des points / landmarks.
        Retourne (label, score_confiance).
        Exemples de labels : 'normal', 'Regarde voisin gauche', 'Regarde voisin droite',
                             'Main sous table', 'Regarde antiseche jambe'.
        """
        if self.model is None:
            return "normal", 1.0

        try:
            feats = extract_features(points_or_landmarks).reshape(1, -1)
            pred = self.model.predict(feats)[0]
            confidence = 1.0

            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(feats)[0]
                confidence = float(np.max(probs))

            if confidence < min_confidence:
                return "normal", confidence

            return str(pred), confidence
        except Exception as e:
            return "normal", 0.0


# Instance globale partagée
_classifier_instance = None


def get_classifier():
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = PostureClassifier()
    return _classifier_instance
