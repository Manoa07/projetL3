from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from DB.database import Base, engine
from models import (
    professeur, salle, matiere, presence_cours, image_capture, detection,
    surveillance_examen, presence_examen,
)
from routes import (
    route_camera,
    route_cours,
    route_detection,
    route_eleve,
    route_examen,
    route_image_capture,
    route_matiere,
    route_presence,
    route_presence_cours,
    route_presence_examen,
    route_professeur,
    route_salle,
    route_stats,
    route_surveillance,
    route_surveillance_examen,
)

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(route_eleve.router)
app.include_router(route_presence.router)
app.include_router(route_cours.router)
app.include_router(route_examen.router)
app.include_router(route_surveillance.router)
app.include_router(route_camera.router)
app.include_router(route_professeur.router)
app.include_router(route_salle.router)
app.include_router(route_stats.router)
app.include_router(route_matiere.router)
app.include_router(route_presence_cours.router)
app.include_router(route_presence_examen.router)
app.include_router(route_image_capture.router)
app.include_router(route_detection.router)
app.include_router(route_surveillance_examen.router)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "upload"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="eleve_upload")
