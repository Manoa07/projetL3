import os
import sqlite3
import time
import datetime

from insightface.app import FaceAnalysis
import cv2

try:
    import face_recognition  # type: ignore
except Exception as e:
    print(e)  # pragma: no cover
    face_recognition = None
    _FACE_IMPORT_ERROR = e
else:
    _FACE_IMPORT_ERROR = None


def _db_path():
    # Use the DB at the repo root: D:/ProjetL3/presence.sql (stable regardless of cwd).
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presence.sql"))


def _repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _resolve_photo_path(photo_path: str) -> str:
    """
    Resolve a photo path stored in DB:
    - absolute path: keep as-is
    - relative path: first try relative to repo root
    - if still not found: try repo_root/image/<photo_path>
    """
    if os.path.isabs(photo_path):
        return photo_path

    root = _repo_root()
    candidate = os.path.join(root, photo_path)
    if os.path.exists(candidate):
        return candidate

    candidate2 = os.path.join(root, "image", photo_path)
    if os.path.exists(candidate2):
        return candidate2

    return candidate  # default best-effort


def _normalize_photo_for_db(photo: str) -> str:
    """
    Normalize user input so 'photo' can be just a filename in image/.
    Prefer storing a relative path like 'image/<file>' when possible.
    """
    if os.path.isabs(photo):
        return photo

    root = _repo_root()
    as_rel = os.path.join(root, photo)
    if os.path.exists(as_rel):
        return photo

    in_image = os.path.join(root, "image", photo)
    if os.path.exists(in_image):
        return os.path.join("image", photo)

    return photo


def get_conn():
    conn = sqlite3.connect(_db_path())
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Etudiants (
            idEtudiant INTEGER PRIMARY KEY AUTOINCREMENT,
            Nom TEXT NOT NULL,
            Prenom TEXT NOT NULL,
            NombreAbsences INTEGER DEFAULT 0,
            NombreRetards INTEGER DEFAULT 0,
            NombrePresences INTEGER DEFAULT 0,
            Photo TEXT NOT NULL
        )
        """
    )

    # Lightweight migrations for existing DBs (SQLite doesn't auto-add columns).
    cur.execute("PRAGMA table_info(Etudiants)")
    existing_cols = {row[1] for row in cur.fetchall()}  # row[1] = column name
    if "NombrePresences" not in existing_cols:
        cur.execute("ALTER TABLE Etudiants ADD COLUMN NombrePresences INTEGER DEFAULT 0")

    # Presence table: one row per student per day (de-dup by UNIQUE).
    # If an older/broken schema exists, migrate it in-place.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Presence'")
    presence_exists = cur.fetchone() is not None

    if not presence_exists:
        cur.execute(
            """
            CREATE TABLE Presence (
                idPresence INTEGER PRIMARY KEY AUTOINCREMENT,
                idEtudiant INTEGER NOT NULL,
                Date_presence TEXT NOT NULL,
                Heure_presence TEXT NOT NULL,
                Status_presence TEXT NOT NULL,
                FOREIGN KEY (idEtudiant) REFERENCES Etudiants (idEtudiant),
                UNIQUE (idEtudiant, Date_presence)
            )
            """
        )
    else:
        cur.execute("PRAGMA table_info(Presence)")
        cols = cur.fetchall()
        # PRAGMA columns: (cid, name, type, notnull, dflt_value, pk)
        col_by_name = {c[1]: c for c in cols}
        pk_col = None
        for c in cols:
            if int(c[5]) == 1:
                pk_col = c[1]
                break

        needs_migration = (
            "idPresence" not in col_by_name
            or "idEtudiant" not in col_by_name
            or pk_col != "idPresence"
        )

        if needs_migration:
            # Create new correct table, copy best-effort data, swap.
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Presence_new (
                    idPresence INTEGER PRIMARY KEY AUTOINCREMENT,
                    idEtudiant INTEGER NOT NULL,
                    Date_presence TEXT NOT NULL,
                    Heure_presence TEXT NOT NULL,
                    Status_presence TEXT NOT NULL,
                    FOREIGN KEY (idEtudiant) REFERENCES Etudiants (idEtudiant),
                    UNIQUE (idEtudiant, Date_presence)
                )
                """
            )
            # Copy only the columns that exist in the old table.
            cur.execute(
                """
                INSERT OR IGNORE INTO Presence_new (idEtudiant, Date_presence, Heure_presence, Status_presence)
                SELECT idEtudiant, Date_presence, Heure_presence, Status_presence
                FROM Presence
                """
            )
            cur.execute("DROP TABLE Presence")
            cur.execute("ALTER TABLE Presence_new RENAME TO Presence")

    # Ensure a UNIQUE index exists even if the table was created earlier without it.
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_presence_student_day
        ON Presence (idEtudiant, Date_presence)
        """
    )
    conn.commit()


def ajouter_etudiant(nom: str, prenom: str, photo: str) -> int:
    """
    Add a student with an image path (Photo).
    Returns the created student's idEtudiant.
    """
    with get_conn() as conn:
        init_db(conn)
        cur = conn.cursor()
        photo_db = _normalize_photo_for_db(photo)
        cur.execute(
            """
            INSERT INTO Etudiants (Nom, Prenom, Photo)
            VALUES (?, ?, ?)
            """,
            (nom, prenom, photo_db),
        )
        conn.commit()
        return int(cur.lastrowid)


def supprimer_etudiant(id_etudiant: int) -> bool:
    """
    Delete a student (and their Presence rows) by idEtudiant.
    Returns True if a student row was deleted, else False.
    """
    with get_conn() as conn:
        init_db(conn)
        cur = conn.cursor()

        # Keep DB consistent even if FK constraints were disabled earlier.
        cur.execute("DELETE FROM Presence WHERE idEtudiant = ?", (id_etudiant,))
        cur.execute("DELETE FROM Etudiants WHERE idEtudiant = ?", (id_etudiant,))
        conn.commit()
        return cur.rowcount > 0


def _load_known_faces(conn: sqlite3.Connection):
    if face_recognition is None:
        # Caller may choose to run detection-only mode.
        return [], [], []

    cur = conn.cursor()
    cur.execute("SELECT idEtudiant, Prenom, Photo FROM Etudiants")
    rows = cur.fetchall()

    known_encodings = []
    known_ids = []
    known_labels = []  # ne contient que le prénom pour l'affichage

    for (sid, prenom, photo_path) in rows:
        full_path = _resolve_photo_path(photo_path)

        if not os.path.exists(full_path):
            continue

        try:
            img = face_recognition.load_image_file(full_path)
            encs = face_recognition.face_encodings(img)
        except Exception:
            continue

        if len(encs) != 1:
            # Skip ambiguous photos (no face or multiple faces).
            continue

        known_encodings.append(encs[0])
        known_ids.append(int(sid))
        known_labels.append(prenom.strip())  # seulement le prénom

    return known_encodings, known_ids, known_labels


def _mark_present_once(conn: sqlite3.Connection, student_id: int):
    """
    Inserts presence for today if missing; increments NombrePresences only when inserted.
    Returns True if it was a new 'present' for today, False if it already existed.
    """
    today = datetime.date.today().isoformat()
    now_t = datetime.datetime.now().time().strftime("%H:%M:%S")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO Presence (idEtudiant, Date_presence, Heure_presence, Status_presence)
        VALUES (?, ?, ?, 'Present')
        """,
        (student_id, today, now_t),
    )
    inserted = cur.rowcount == 1

    if inserted:
        cur.execute(
            """
            UPDATE Etudiants
            SET NombrePresences = COALESCE(NombrePresences, 0) + 1
            WHERE idEtudiant = ?
            """,
            (student_id,),
        )
        conn.commit()

    return inserted


def verifier_presence(tolerance: float = 0.4, camera_index: int = 0):
    """
    Live webcam:
    - Detect + recognize faces with a stricter tolerance (0.4 by default) for higher precision.
    - If recognized and in DB: display 'Present - <prenom>' and mark attendance once per day.
    - If not recognized: keep streaming.
    - Exit with 'q'.
    """
    # If face_recognition isn't installed, keep the webcam running in detection-only mode.
    if face_recognition is None:
        return verifier_presence_detection_only(camera_index=camera_index)

    with get_conn() as conn:
        init_db(conn)
        known_encodings, known_ids, known_labels = _load_known_faces(conn)

        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise RuntimeError("Cannot open webcam.")

        last_seen = {}  # student_id -> last_mark_ts (avoid rapid repeats even with DB IGNORE)
        min_mark_interval_s = 9000.0  # 2.5 heures

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if face_recognition is None:
                break

            # Speed-up: downscale for recognition, then scale boxes back.
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back up.
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                label = "Unknown"
                color = (0, 0, 255)

                if known_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=tolerance)
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                    best_idx = None
                    if len(face_distances) > 0:
                        best_idx = int(face_distances.argmin())

                    if best_idx is not None and matches[best_idx]:
                        student_id = known_ids[best_idx]
                        student_label = known_labels[best_idx]  # prénom uniquement

                        now = time.time()
                        if now - last_seen.get(student_id, 0) >= min_mark_interval_s:
                            _mark_present_once(conn, student_id)
                            last_seen[student_id] = now

                        label = f"Present - {student_label}"
                        color = (0, 255, 0)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                cv2.putText(
                    frame,
                    label,
                    (left + 6, bottom - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    2,
                )

            cv2.imshow("Verification de Presence", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


def verifier_presence_detection_only(camera_index: int = 0):
    """
    Webcam loop when face_recognition isn't installed:
    - Detect faces (no identification)
    - Keep streaming until 'q'
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam.")

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(
                frame,
                "Face detectee",
                (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

        cv2.imshow("Verification de Presence", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    #verifier_presence()
    verifier_presence_detection_only()