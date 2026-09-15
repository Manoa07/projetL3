from typing import Annotated
import os

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import declarative_base

# WARN-10 : charger .env automatiquement si python-dotenv est disponible
try:
    from dotenv import load_dotenv
    from pathlib import Path as _Path
    # Chercher .env depuis le répertoire courant jusqu'à la racine du projet
    _env_file = _Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(dotenv_path=_env_file)
    else:
        load_dotenv()
except ImportError:
    pass
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL doit être défini avec une URL PostgreSQL "
        "(par exemple postgresql+psycopg2://user:password@localhost/dbname)."
    )
if not DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://")):
    raise RuntimeError("DATABASE_URL doit utiliser PostgreSQL.")

engine = create_engine(DATABASE_URL, connect_args={"options": "-c client_encoding=UTF8"})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependancy= Annotated[Session,Depends(get_db)]
