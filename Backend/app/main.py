from typing import Annotated, List

from uuid import uuid4
from fastapi import Depends, FastAPI
from schema.sch_eleve import Create_eleve
from DB.database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
from sqlalchemy import Integer, Column,String,Boolean,ForeignKey,Date
import routes.route_eleve, routes.route_cours ,routes.route_presence


app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(routes.route_eleve.router)
app.include_router(routes.route_presence.router)
app.include_router(routes.route_cours.router)




