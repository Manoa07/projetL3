from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from DB.database import Base


class Matiere(Base):
    __tablename__ = "matiere"
    id_matiere = Column(Integer, primary_key=True, autoincrement=True)
    nom_matiere = Column(String(150), nullable=False, unique=True)
    cours = relationship("Cours", back_populates="matiere")
    examens = relationship("Examen", back_populates="matiere")
