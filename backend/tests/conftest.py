"""Base de datos de pruebas: SQLite en memoria, sembrada con el universo completo
(IBEX 35 + Dow Jones + Nasdaq-100 + sueltas), para que los tests no toquen ni la BD
real ni internet. El esquema se crea directamente desde los modelos (no hace falta
pasar por Alembic en los tests: eso solo le hace falta a la BD real)."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import get_db
from app.data.universo import universo_completo
from app.main import app
from app.models.base import Base
from app.models.company import Company

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

_db = TestingSessionLocal()
_db.add_all(Company(**c) for c in universo_completo())
_db.commit()
_db.close()


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
