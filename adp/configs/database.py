from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from adp.configs.settings import settings

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# Enable echo in debug mode to aid troubleshooting
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_size=10, 
    max_overflow=20, 
    pool_pre_ping=True,
    echo=bool(settings.DEBUG)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables():
    """Create database tables from SQLAlchemy models.

    Call this on application startup (safe to call repeatedly).
    """
    from sqlalchemy import inspect

    inspector = inspect(engine)
    # Calling create_all is idempotent; it will only create missing tables
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        