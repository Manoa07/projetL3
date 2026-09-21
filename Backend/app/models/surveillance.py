from DB.database import Base
from sqlalchemy import Integer, Column, String, DateTime, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class Surveillance(Base):
    __tablename__='surveillance'
    __table_args__ = (
        UniqueConstraint(
            'id_eleve',
            'id_examen',
            name='uq_surveillance_eleve_examen',
        ),
    )
    Id_surveillance=Column(Integer,primary_key=True,autoincrement=True,index=True)
    id_eleve=Column(Integer,ForeignKey("eleve.Id_eleve", ondelete="CASCADE"))
    id_examen=Column(Integer,ForeignKey("examen.id_examen", ondelete="CASCADE"))
    Remarque=Column(String)
    Status_examen=Column(String)
    examen=relationship("Examen",back_populates="surveillance")
    eleve=relationship("Eleve",back_populates="surveillance")
    camera=relationship("Camera",back_populates="surveillance")