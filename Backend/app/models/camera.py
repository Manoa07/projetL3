from DB.database import Base
from sqlalchemy import Integer, Column,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship

class Camera(Base):
    __tablename__="camera"
    Id_Capture=Column(Integer,primary_key=True,autoincrement=True,index=True)
    Id_surveillance=Column(Integer,ForeignKey("surveillance.Id_surveillance"))
    Fichier_capture=Column(String)
    surveillance=relationship("Surveillance",back_populates="camera")
    