from sqlalchemy import Column, Integer, String
from DB.database import Base


class Matiere(Base):
    __tablename__ = "matiere"
    id_matiere = Column(Integer, primary_key=True, autoincrement=True)
    nom_matiere = Column(String(150), nullable=False, unique=True)
