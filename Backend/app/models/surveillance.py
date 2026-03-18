from DB.database import Base
from sqlalchemy import Integer, Column,String,DateTime,Time,ForeignKey
from sqlalchemy.orm import relationship

class Surveillance(Base):
    __tablename__='surveillance'
    Id_surveillance=Column(Integer,primary_key=True,autoincrement=True,index=True)
    id_eleve=Column(Integer,ForeignKey("eleve.Id_eleve"))
    id_examen=Column(Integer,ForeignKey("examen.id_examen"))
    Remarque=Column(String)
    Status_examen=Column(String)
    examen=relationship("Examen",back_populates="surveillance")
    eleve=relationship("Eleve",back_populates="surveillance")
    camera=relationship("Camera",back_populates="surveillance")