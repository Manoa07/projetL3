from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql://postgres:YannickDB@localhost:5432/Surveillance_DB"

engine= create_engine(DATABASE_URL)
Base=declarative_base()
Base.metadata.create_all(engine)
