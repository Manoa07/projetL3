import cv2
import numpy as np
from mtcnn import MTCNN
from datetime import datetime, timedelta
import pickle
from keras_facenet import FaceNet
import requests
class SystemePresence:
    """
    Système de présence par reconnaissance faciale utilisant l'API PostgreSQL.
    """
    def __init__(self, seuil_distance=0.8):
        """
        Initialise les modèles et la connexion à la base.

        Args:
            seuil_distance (float): Seuil de distance pour considérer une correspondance.
        """
        self.seuil = seuil_distance
        self.detector = MTCNN()
        # Modèle d'embedding
        print("Chargement du modèle FaceNet (keras-facenet)...")
        self.embedder = FaceNet()
        print("Modèle chargé avec succès.")
        # Charger la base des embeddings (cache)
        self.base_visages = self.charger_base()
        # Dictionnaire pour éviter les enregistrements trop fréquents (2h30)
        self.dernier_enregistrement = {}  # {nom_complet: datetime}


    def charger_base(self):
        """Charge les embeddings depuis la base pour la comparaison rapide."""
        try:
            reponse = requests.get("http://localhost:8000/eleve/all")
            eleves = reponse.json()
            base = {}
            for eleve in eleves:
                nom_complet = f"{eleve['Nom_eleve']} {eleve['Prenom_eleve']} "
                # BUG-13 : ignorer les élèves sans embedding pour éviter crash numpy
                if eleve.get("embedding") is None:
                    continue
                embedding = np.array(eleve["embedding"])
                base[nom_complet] = (eleve["Numero_eleve"], embedding)
            return base
        except Exception as e:
            print(e)
            return {}

        

    def obtenir_embedding(self, image_visage):
        """Calcule l'embedding d'un visage."""
        return self.embedder.embeddings([image_visage])[0]

    def comparer_visage(self, embedding):
        """
        Compare un embedding avec la base de données.

        Returns:
            tuple: (nom_complet, distance, id_eleve) ou (None, None, None)
        """
        if not self.base_visages:
            return None, None, None

        min_dist = float('inf')
        identite = None
        id_eleve = None

        for nom, (eid, emb_ref) in self.base_visages.items():
            dist = np.linalg.norm(embedding - emb_ref)
            if dist < min_dist:
                min_dist = dist
                identite = nom
                id_eleve = eid

        if min_dist < self.seuil:
            return identite, min_dist, id_eleve
        else:
            return None, None, None

    def enregistrer_presence_db(self, id_eleve, nom_complet):

        maintenant = datetime.now()

        data={
            "id_eleve": id_eleve,
            "id_cours": 1,
            "Date_presence": maintenant.date().isoformat(),
            "Heure_presence": maintenant.time().isoformat(),
            "Status_presence": "present"
        }
        try:
            reponse=requests.post(
                "http://localhost:8000/presence/create",
                json=data
            )
            if reponse.status_code==200:
                print(f"Présence enregistrée pour {nom_complet}")
            else:
                print("Erreur API : ",reponse.text)
        except Exception as e:
            print(e)

    def run(self, source=0):
        """
        Lance la boucle principale de reconnaissance.
        """
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print("Erreur : impossible d'ouvrir la caméra.")
            return

        print("Démarrage de la reconnaissance. Appuyez sur 'q' pour quitter.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

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
                nom, dist, id_eleve = self.comparer_visage(embedding)

                if nom:
                    maintenant = datetime.now()
                    if nom in self.dernier_enregistrement:
                        delta = maintenant - self.dernier_enregistrement[nom]
                        if delta < timedelta(hours=2, minutes=30):
                            # Trop tôt, on n'enregistre pas
                            label = f"{nom} (déjà présent)"
                            couleur = (0, 255, 255)  # Jaune
                        else:
                            # Intervalle dépassé, on enregistre
                            self.enregistrer_presence_db(id_eleve, nom)
                            self.dernier_enregistrement[nom] = maintenant
                            label = f"{nom} ({dist:.2f})"
                            couleur = (0, 255, 0)  # Vert
                    else:
                        # Première détection
                        self.enregistrer_presence_db(id_eleve, nom)
                        self.dernier_enregistrement[nom] = maintenant
                        label = f"{nom} ({dist:.2f})"
                        couleur = (0, 255, 0)
                else:
                    label = "Inconnu"
                    couleur = (0, 0, 255)  # Rouge

                cv2.rectangle(frame, (x, y), (x+w, y+h), couleur, 2)
                cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, couleur, 2)

            cv2.imshow('Systeme de Presence', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def ajouter_eleve(self, nom, prenom, classe ,numero,images_visages):
 
        embeddings = []
        for img in images_visages:
            emb = self.obtenir_embedding(img)
            embeddings.append(emb)

        emb_moyen = np.mean(embeddings, axis=0)

        _, buffer = cv2.imencode(".jpg", images_visages[0])
        files = {
            "photo": ("photo.jpg", buffer.tobytes(), "image/jpeg")
        }
        data = {
            "Nom_eleve": nom,
            "Prenom_eleve": prenom,
            "Classe_eleve": classe,
            "Numero_eleve": numero,
            "embedding": emb_moyen.tolist()
        }
        try:
            response = requests.post(
            "http://localhost:8000/eleve/create",
            data=data,
            files=files
            )
            print(response.json())
        except Exception as e:
            print(f"Erreur lors de l'ajout : {e}")


def capturer_images_visage(detector, nb_images=10):
    """
    Ouvre la caméra et capture plusieurs images du visage.
    Retourne la liste des images RGB.
    """
    cap = cv2.VideoCapture(0)
    images = []
    print(f"Appuyez sur 'c' pour capturer ({nb_images} fois idéalement), 'q' pour quitter.")
    while len(images) < nb_images:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Capture', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = detector.detect_faces(rgb)
            if faces:
                x, y, w, h = faces[0]['box']
                x, y = max(0, x), max(0, y)
                face_img = rgb[y:y+h, x:x+w]
                images.append(face_img)
                print(f"Capture {len(images)}/{nb_images}")
            else:
                print("Aucun visage détecté.")
        elif key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return images


if __name__ == "__main__":
    systeme = SystemePresence(seuil_distance=0.8)

    print("\n=== SYSTÈME DE PRÉSENCE ===")
    print("1. Ajouter un élève")
    print("2. Lancer la reconnaissance")
    choix = input("Votre choix (1 ou 2) : ")

    if choix == "1":
        nom = input("Nom de l'élève : ")
        prenom = input("Prénom de l'élève : ")
        classe=input("Classe de l'élève : ")
        numero=int(input("Numero de l'élève : "))
        print("Préparez-vous à être photographié.")
        images_visages = capturer_images_visage(systeme.detector, nb_images=10)
        if len(images_visages) >= 3:
            systeme.ajouter_eleve(nom, prenom, classe, numero, images_visages)
        else:
            print("Pas assez d'images valides.")
    elif choix == "2":
        systeme.run()
    else:
        print("Choix invalide.")
