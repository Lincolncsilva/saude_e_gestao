from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

load_dotenv()

# CONFIGURAÇÃO
REQUIRED_ENVS = ["API_USER", "API_PASSWORD", "HOST", "PORTA", "POSTGRES_DB"]
missing = [k for k in REQUIRED_ENVS if not os.getenv(k)]
if missing:
    raise RuntimeError(f"Variáveis de ambiente faltando: {', '.join(missing)}")

user = os.getenv("API_USER")
pswd = os.getenv("API_PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORTA")
db   = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{user}:{pswd}@{host}:{port}/{db}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def session_local():
    return SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
