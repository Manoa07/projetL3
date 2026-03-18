from DB.database import Base
from sqlalchemy import Integer, Column,String,DateTime,Time,ForeignKey
from sqlalchemy.orm import relationship

class Examen(Base):
    __tablename__ ='examen'
    id_examen=Column(Integer,primary_key=True,autoincrement=True,index=True)
    id_cours=Column(Integer,ForeignKey("cours.Id_cours"))
    date_examen=Column(DateTime)
    Heure_debut=Column(Time)
    Heure_fin=Column(Time)
    Salle_examen=Column(String)
    cours=relationship("Cours",back_populates="examen")
    surveillance=relationship("Surveillance",back_populates="examen")