from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from DB.database import Base


class Professeur(Base):
    __tablename__ = "professeur"
    id_professeur = Column(Integer, primary_key=True, autoincrement=True)
    nom_professeur = Column(String(100), nullable=False)
    prenom_professeur = Column(String(100), nullable=False)
    matricule_professeur = Column(Integer, unique=True, nullable=False)
    cours = relationship("Cours", back_populates="professeur")
