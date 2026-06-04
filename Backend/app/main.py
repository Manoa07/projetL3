from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from DB.database import Base, engine
from routes import (
    route_camera,
    route_cours,
    route_eleve,
    route_examen,
    route_presence,
    route_surveillance,
)

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(route_eleve.router)
app.include_router(route_presence.router)
app.include_router(route_cours.router)
app.include_router(route_examen.router)
app.include_router(route_surveillance.router)
app.include_router(route_camera.router)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "upload"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="eleve_upload")
