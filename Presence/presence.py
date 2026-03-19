import cv2
import numpy as np
from mtcnn import MTCNN
from datetime import datetime, timedelta
import pickle
from keras_facenet import FaceNet
import sqlite3

class SystemePresence:
    """
    Système de présence par reconnaissance faciale avec base SQLite.
    """

    def __init__(self, seuil_distance=0.8, db_path='presence.db'):
        """
        Initialise les modèles et la connexion à la base.

        Args:
            seuil_distance (float): Seuil de distance pour considérer une correspondance.
            db_path (str): Chemin vers le fichier SQLite.
        """
        self.seuil = seuil_distance
        self.db_path = db_path

        # Connexion à la base
        self.conn = self.connect_db()
        self.creer_tables()

        # Détecteur de visages MTCNN
        self.detector = MTCNN()

        # Modèle d'embedding
        print("Chargement du modèle FaceNet (keras-facenet)...")
        self.embedder = FaceNet()
        print("Modèle chargé avec succès.")

        # Charger la base des embeddings (cache)
        self.base_visages = self.charger_base()

        # Dictionnaire pour éviter les enregistrements trop fréquents (2h30)
        self.dernier_enregistrement = {}  # {nom_complet: datetime}

    def connect_db(self):
        """Établit la connexion SQLite."""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            print("Connexion à SQLite établie.")
            return conn
        except Exception as e:
            print(f"Erreur de connexion : {e}")
            return None

    def creer_tables(self):
        """Crée les tables si elles n'existent pas."""
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS eleves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom VARCHAR(100) NOT NULL,
                prenom VARCHAR(100) NOT NULL,
                embedding BLOB NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS presences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_eleve INTEGER REFERENCES eleves(id) ON DELETE CASCADE,
                date_presence DATE NOT NULL,
                heure_presence TIME NOT NULL,
                UNIQUE(id_eleve, date_presence)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS absences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_eleve INTEGER REFERENCES eleves(id) ON DELETE CASCADE,
                date_absence DATE NOT NULL,
                justifie BOOLEAN DEFAULT FALSE,
                UNIQUE(id_eleve, date_absence)
            )
        """)
        self.conn.commit()
        cur.close()
        print("Tables vérifiées/créées.")

    def charger_base(self):
        """Charge les embeddings depuis la base pour la comparaison rapide."""
        if not self.conn:
            return {}
        cur = self.conn.cursor()
        cur.execute("SELECT id, nom, prenom, embedding FROM eleves")
        rows = cur.fetchall()
        cur.close()
        base = {}
        for row in rows:
            emb_blob = row[3]
            emb = pickle.loads(emb_blob)
            nom_complet = f"{row[1]} {row[2]}"
            base[nom_complet] = (row[0], emb)
        return base

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
        """
        Enregistre la présence dans la table presences.
        Vérifie d'abord si l'élève n'a pas déjà une présence aujourd'hui (unicité).
        """
        maintenant = datetime.now()
        date_auj = maintenant.date().isoformat()
        heure_act = maintenant.time().isoformat()

        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO presences (id_eleve, date_presence, heure_presence)
                VALUES (?, ?, ?)
            """, (id_eleve, date_auj, heure_act))
            self.conn.commit()
            print(f"Présence enregistrée pour {nom_complet} à {heure_act}")
        except sqlite3.IntegrityError:
            self.conn.rollback()
            print(f"{nom_complet} a déjà une présence aujourd'hui.")
        finally:
            cur.close()

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

    def ajouter_eleve(self, nom, prenom, images_visages):
        """
        Ajoute un nouvel élève dans la base.
        - Calcule l'embedding moyen à partir des images fournies.
        - Stocke dans la table eleves.
        - Met à jour le cache local.
        """
        embeddings = []
        for img in images_visages:
            emb = self.obtenir_embedding(img)
            embeddings.append(emb)
        emb_moyen = np.mean(embeddings, axis=0)
        emb_blob = pickle.dumps(emb_moyen)

        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO eleves (nom, prenom, embedding)
                VALUES (?, ?, ?)
            """, (nom, prenom, emb_blob))
            self.conn.commit()
            new_id = cur.lastrowid
            print(f"Élève '{nom} {prenom}' ajouté avec l'id {new_id}.")
            nom_complet = f"{nom} {prenom}"
            self.base_visages[nom_complet] = (new_id, emb_moyen)
        except Exception as e:
            self.conn.rollback()
            print(f"Erreur lors de l'ajout : {e}")
        finally:
            cur.close()


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
    db_path = 'presence.db'
    systeme = SystemePresence(seuil_distance=0.8, db_path=db_path)

    print("\n=== SYSTÈME DE PRÉSENCE ===")
    print("1. Ajouter un élève")
    print("2. Lancer la reconnaissance")
    choix = input("Votre choix (1 ou 2) : ")

    if choix == "1":
        nom = input("Nom de l'élève : ")
        prenom = input("Prénom de l'élève : ")
        print("Préparez-vous à être photographié.")
        images = capturer_images_visage(systeme.detector, nb_images=10)
        if len(images) >= 3:
            systeme.ajouter_eleve(nom, prenom, images)
        else:
            print("Pas assez d'images valides.")
    elif choix == "2":
        systeme.run()
    else:
        print("Choix invalide.")