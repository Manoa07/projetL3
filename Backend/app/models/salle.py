from sqlalchemy import Column, Integer, String
from DB.database import Base


class Salle(Base):
    __tablename__ = "salle"
    id_salle = Column(Integer, primary_key=True, autoincrement=True)
    nom_salle = Column(String(100), nullable=False, unique=True)
