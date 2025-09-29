from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import Config


# --- Base for models ---
class Base(DeclarativeBase):
    pass


# --- Engine & session factory ---
engine = create_engine(
    Config.DATABASE_URL,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


# --- Dependency for FastAPI ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Utility: init tables ---
def init_db():
    """Create tables if they don't exist (for dev/demo)."""
    # pylint: disable-next=import-outside-toplevel, cyclic-import
    import dsw_bootstrapper.models
    print(f"Loaded: {dsw_bootstrapper.models}")
    Base.metadata.create_all(bind=engine)
