import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Configure SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models (modern SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass

# Dependency to get a database session
def get_db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
        db.commit() # Commit si tout s'est bien passé dans l'endpoint
    except Exception:
        db.rollback() # Rollback en cas d'erreur
        raise
    finally:
        db.close()
        logger.debug("Database session closed")