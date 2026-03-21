from DB.database import Base
from sqlalchemy import Integer, Column,String,ForeignKey
from sqlalchemy import Date,Time 
from sqlalchemy.orm import relationship


class Presence(Base):
    __tablename__= 'presence'
    id_presence=Column(Integer,primary_key=True,autoincrement=True,index=True)
    id_cours=Column(Integer,ForeignKey("cours.Id_cours",ondelete="CASCADE"))
    id_eleve=Column(Integer,ForeignKey("eleve.Id_eleve",ondelete="CASCADE"))
    Status_presence=Column(String(50),nullable=False)
    Heure_presence=Column(Time,nullable=False)
    Date_presence=Column(Date,nullable=False)
    cours = relationship("Cours",back_populates="presence")
    eleve = relationship("Eleve",back_populates="presence")