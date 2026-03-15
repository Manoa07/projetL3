from unittest.mock import Base

from sqlalchemy import Integer, column


class eleve(Base):
    id=column(Integer,primary_key=True)