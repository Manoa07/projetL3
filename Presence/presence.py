import cv2
import mediapipe as mp
import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('presence.sql')
cursor = conn.cursor()

# Création de la table si elle n'existe pas déjà
cursor.execute('''
CREATE TABLE IF NOT EXISTS Etudiants (
    idEtudiant INTEGER PRIMARY KEY AUTOINCREMENT,
    Nom TEXT NOT NULL,
    Prenom TEXT NOT NULL,
    NombreAbsences INTEGER DEFAULT 0,
    NombreRetards INTEGER DEFAULT 0,
    Photo TEXT NOT NULL
)
''')
conn.commit()

# Fonction pour détecter et reconnaître les visages
def detecter_presence():
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            # Ici, vous pouvez ajouter la logique pour comparer le visage détecté avec les photos dans la base de données

        cv2.imshow('Presence Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Fonction pour vérifier la présence d'un étudiant en continu
def verifier_presence():
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            cv2.putText(frame, "Etudiant present", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Etudiant absent", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow('Verification de Presence', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 correspond à la touche "esc"
            break

    cap.release()
    cv2.destroyAllWindows()

# Exemple d'ajout d'un étudiant dans la base de données
def ajouter_etudiant(idEtudiant, nom, prenom, photo):
    cursor.execute('''
    INSERT INTO Etudiants (idEtudiant, Nom, Prenom, Photo)
    VALUES (?, ?, ?, ?)
    ''', (idEtudiant, nom, prenom, photo))
    conn.commit()



# Exemple d'utilisation
#ajouter_etudiant(1, 'Dupont', 'Jean', 'image\mark-zuckerberg-at-g8-in-deauville-france.webp')
detecter_presence()
#verifier_presence()

# Fermeture de la connexion à la base de données
# conn.close()






