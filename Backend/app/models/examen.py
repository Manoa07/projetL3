from DB.database import Base
from sqlalchemy import Integer, Column, String, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship

class Examen(Base):
    __tablename__ ='examen'
    id_examen=Column(Integer,primary_key=True,autoincrement=True,index=True)
    id_cours=Column(Integer,ForeignKey("cours.Id_cours"))
    date_examen=Column(DateTime)
    Heure_debut=Column(Time)
    Heure_fin=Column(Time)
    Salle_examen=Column(String)
    semestre_examen=Column(String(30), nullable=True)
    id_salle_salle=Column(Integer, ForeignKey("salle.id_salle"), nullable=True)
    id_matiere_matiere=Column(Integer, ForeignKey("matiere.id_matiere"), nullable=True)
    cours=relationship("Cours",back_populates="examen")
    surveillance=relationship("Surveillance",back_populates="examen")
