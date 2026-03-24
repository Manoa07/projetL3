import json
import cv2
import numpy as np
from mtcnn import MTCNN
from datetime import datetime, timedelta
import pickle 
from  keras_facenet import FaceNet
from services.presence_service import create_presence
from services.eleve_service import get_eleve
from models.presence import Presence

class SystemePresence:

    def __init__(self ,id_cours, db, seuil_distance=0.8):
        self.db=db
        self.id_cours=id_cours
        self.seuil = seuil_distance
        self.detector = MTCNN()
        self.base_visages = self.charger_base()
        self.dernier_enregistrement = {} 
        self.embedder = FaceNet()
        
        


    def charger_base(self):
        eleves=get_eleve(self.db)
        base={}
        for eleve in eleves:
            nom_complet = f"{eleve['Nom_eleve']} {eleve['Prenom_eleve']}"
            embedding=eleve['embedding']
            if embedding is None:
                continue
            if isinstance(embedding,bytes):
                try:
                    embedding=pickle.loads(embedding)
                except Exception as e:
                    print("Erreur dans pickle : ", e)
                    continue
            try:
                embedding=np.array(embedding, dtype=np.float32)
            except Exception as e:
                print("Erreur conversion numpy : ",e)
                continue
            base[nom_complet]=(eleve['Id_eleve'],eleve['Classe_eleve'],self.id_cours,embedding)
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

    def enregistrer_presence_db(self, Id_eleve,Id_cours,Classe_eleve):

        maintenant = datetime.now()
        date_auj = maintenant.date().isoformat()
        heure_act = maintenant.time().isoformat()

        data=Presence(
            id_eleve=Id_eleve,
            id_cours=Id_cours,
            Date_presence=date_auj,
            Heure_presence=heure_act,
            Status_presence="present"
        )

        
        try:
            reponse=create_presence(data,self.db)
            if reponse:
                print("presence enregistrer")
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
                nom_complet, mindist, id_eleve,id_cours,classe_eleve = self.comparer_visage(embedding)
    
                if nom_complet:
                    maintenant = datetime.now()
                    if nom_complet in self.dernier_enregistrement:
                        delta = maintenant - self.dernier_enregistrement[nom_complet]
                        if delta < timedelta(hours=2, minutes=30):
                            print(f"{nom_complet} (déjà présent)")
                            
                        else:
                            # Intervalle dépassé, on enregistre
                            self.enregistrer_presence_db(id_eleve,id_cours, classe_eleve)
                            self.dernier_enregistrement[nom_complet] = maintenant
                            resultat.append({
                                "nom" : nom_complet,
                                "id_eleve" : id_eleve,
                                "id_cours":id_cours,
                                "status" : "present"
                            })
                    else:
                        # Première détection
                        self.enregistrer_presence_db(id_eleve,id_cours,classe_eleve)
                        self.dernier_enregistrement[nom_complet] = maintenant
                        resultat.append({
                            "nom" : nom_complet,
                            "id_eleve" : id_eleve,
                            "id_cours" : id_cours,
                            "status" : "present"
                        })
                else:
                    resultat.append({
                        "status":"inconnu"
                    })
            return resultat
            

