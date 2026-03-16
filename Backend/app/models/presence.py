from DB.database import Base
from sqlalchemy import Integer, Column,String,Boolean,ForeignKey
from sqlalchemy import Date,Time 
from sqlalchemy.orm import relationship


class Presence(Base):
    __tablename__= 'presence'
    id_presence=Column(Integer,primary_key=True,autoincrement=True,index=True)
    id_cours=Column(Integer,ForeignKey("cours.Id_cours"))
    id_eleve=Column(Integer,ForeignKey("eleve.Id_eleve"))
    Status_presence=Column(String)
    Heure_presence=Column(Time)
    Date_presence=Column(Date)
    cours = relationship("Cours",back_populates="presence")
    eleve = relationship("Eleve",back_populates="presence")