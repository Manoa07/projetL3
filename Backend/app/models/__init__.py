from models.professeur import Professeur
from models.salle import Salle
from models.matiere import Matiere
from models.eleve import Eleve
from models.cours import Cours
from models.presence import Presence
from models.presence_cours import PresenceCours
from models.examen import Examen
from models.presence_examen import PresenceExamen
from models.surveillance import Surveillance
from models.surveillance_examen import SurveillanceExamen
from models.camera import Camera
from models.detection import Detection
from models.image_capture import ImageCapture

__all__ = [
    "Professeur",
    "Salle",
    "Matiere",
    "Eleve",
    "Cours",
    "Presence",
    "PresenceCours",
    "Examen",
    "PresenceExamen",
    "Surveillance",
    "SurveillanceExamen",
    "Camera",
    "Detection",
    "ImageCapture",
]
