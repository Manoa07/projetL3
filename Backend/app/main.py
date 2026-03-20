from fastapi import FastAPI
from DB.database import engine,Base
from routes import route_camera,route_cours,route_eleve,route_examen,route_presence,route_surveillance
from fastapi.staticfiles import StaticFiles

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(route_eleve.router)
app.include_router(route_presence.router)
app.include_router(route_cours.router)
app.include_router(route_examen.router)
app.include_router(route_surveillance.router)
app.include_router(route_camera.router)
app.mount("/uploads", StaticFiles(directory="upload"), name="eleve_upload")


