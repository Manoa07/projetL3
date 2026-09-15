import time
import cv2
import numpy as np
from datetime import datetime, timedelta
import pickle
from services.presence_service import create_presence
from services.eleve_service import get_eleve, _get_detector, _get_embedder
from models.presence import Presence  # encore utilisé pour la requête eleves_deja_presents

# Singleton : MTCNN et FaceNet partagés avec eleve_service (WARN-05)
_detector = None
_embedder = None

# Cache en mémoire des embeddings pour éviter les requêtes DB à chaque frame
_cached_eleves_base = None
_cached_time = 0.0
_CACHE_TTL = 15.0  # secondes



def _get_detector_local():
    """Délègue au singleton de eleve_service pour éviter le double chargement."""
    return _get_detector()


def _get_embedder_local():
    """Délègue au singleton de eleve_service pour éviter le double chargement."""
    return _get_embedder()


class SystemePresence:

    def __init__(self, id_cours, db, seuil_distance=0.8):
        self.db = db
        self.id_cours = id_cours
        self.seuil = seuil_distance
        self.detector = _get_detector_local()
        self.embedder = _get_embedder_local()
        self.base_visages = self.charger_base()
        self.dernier_enregistrement = {}
        # Un scan crée une nouvelle instance pour chaque image reçue par
        # l'API. Il faut donc conserver l'état dans la base, sinon le même
        # élève est réenregistré à chaque image.
        aujourd_hui = datetime.now().date()
        self.eleves_deja_presents = {
            id_eleve
            for (id_eleve,) in db.query(Presence.id_eleve).filter(
                Presence.id_cours == self.id_cours,
                Presence.Date_presence == aujourd_hui,
            ).all()
        }
        
        


    def charger_base(self):
        global _cached_eleves_base, _cached_time
        now = time.time()
        if _cached_eleves_base is not None and (now - _cached_time < _CACHE_TTL):
            return {
                nom: (id_e, c_e, self.id_cours, emb)
                for nom, (id_e, c_e, _, emb) in _cached_eleves_base.items()
            }

        eleves = get_eleve(self.db)
        base = {}
        for eleve in eleves:
            nom_complet = f"{eleve['Nom_eleve']} {eleve['Prenom_eleve']}"
            embedding = eleve['embedding']
            if embedding is None:
                continue
            if isinstance(embedding, bytes):
                try:
                    embedding = pickle.loads(embedding)
                except Exception as e:
                    print("Erreur dans pickle : ", e)
                    continue
            try:
                embedding = np.array(embedding, dtype=np.float32)
            except Exception as e:
                print("Erreur conversion numpy : ", e)
                continue
            base[nom_complet] = (eleve['Id_eleve'], eleve['Classe_eleve'], self.id_cours, embedding)

        _cached_eleves_base = base
        _cached_time = now
        return base

    def obtenir_embedding(self, image_visage):
        return self.embedder.embeddings([image_visage])[0]

    def comparer_visage(self, embedding):
        if not self.base_visages:
            return None, None, None ,None,None

        min_dist = float('inf')
        Nom_complet = None
        id_c=None
        id_e = None
        C_e=None

        for nom_complet, (id_e , C_e,id_c, emb_ref) in self.base_visages.items():
            if emb_ref is None : 
                continue
            dist = np.linalg.norm(embedding - emb_ref)
            if dist < min_dist:
                min_dist = dist
                Nom_complet = nom_complet
                Id_cours=id_c
                Id_eleve = id_e
                Classe_eleve=C_e
            

        if min_dist < self.seuil:
            return Nom_complet, min_dist, Id_eleve ,Id_cours,Classe_eleve
        else:
            return None, None, None ,None,None

    def enregistrer_presence_db(self, Id_eleve, Id_cours, Classe_eleve):
        """BUG-05 : on passe un schéma Pydantic Create_presence, pas un objet ORM."""
        from schema.sch_presence import Create_presence
        import datetime as dt

        maintenant = dt.datetime.now()

        data = Create_presence(
            id_eleve=Id_eleve,
            id_cours=Id_cours,
            Date_presence=maintenant.date(),
            Heure_presence=maintenant.time().replace(microsecond=0),
            Status_presence="present",
        )

        try:
            reponse = create_presence(data, self.db)
            if reponse:
                print(f"Présence enregistrée pour l'élève {Id_eleve}")
        except Exception as e:
            raise e

    def traiter_image(self, frame):
            resultat=[]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            try:
                detections = self.detector.detect_faces(rgb_frame)
            except Exception as e:
                print(f"Erreur de détection (ignorée) : {e}")
                detections = []

            for det in detections:
                x, y, w, h = det['box']
                x, y = max(0, x), max(0, y)
                w = min(w, frame.shape[1] - x)
                h = min(h, frame.shape[0] - y)

                face = rgb_frame[y:y+h, x:x+w]
                if face.size == 0:
                    continue

                embedding = self.obtenir_embedding(face)
                if embedding is None:
                    continue
                nom_complet, mindist, id_eleve, id_cours, classe_eleve = self.comparer_visage(embedding)
    
                if nom_complet:
                    maintenant = datetime.now()
                    resultat_entry = {
                        "nom": nom_complet,
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h,
                        "id_eleve": id_eleve,
                        "id_cours": id_cours,
                        "status": "present"
                    }

                    # Une présence est unique par élève, cours et journée.
                    # On garde le visage affiché, mais on ne tente plus de
                    # créer une nouvelle présence en base.
                    if id_eleve in self.eleves_deja_presents:
                        print(f"{nom_complet} (déjà présent pour ce cours aujourd'hui)")
                        resultat_entry["deja_present"] = True
                        resultat.append(resultat_entry)
                        continue

                    if nom_complet in self.dernier_enregistrement:
                        delta = maintenant - self.dernier_enregistrement[nom_complet]
                        if delta < timedelta(hours=2, minutes=30):
                            print(f"{nom_complet} (déjà présent)")
                            # On ajoute quand même les coordonnées pour l'affichage
                            resultat_entry["deja_present"] = True
                            resultat.append(resultat_entry)
                        else:
                            self.enregistrer_presence_db(id_eleve, id_cours, classe_eleve)
                            self.eleves_deja_presents.add(id_eleve)
                            self.dernier_enregistrement[nom_complet] = maintenant
                            resultat.append(resultat_entry)
                    else:
                        self.enregistrer_presence_db(id_eleve, id_cours, classe_eleve)
                        self.eleves_deja_presents.add(id_eleve)
                        self.dernier_enregistrement[nom_complet] = maintenant
                        resultat.append(resultat_entry)
                else:
                    resultat.append({
                        "status": "inconnu",
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h
                    })
            return resultat
            
