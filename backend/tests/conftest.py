import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import DATABASE_URL, get_db
from app.main import app

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def db_session_rollback():
    """
    Transactional fixture: Wraps each test in an isolated connection-level transaction
    that automatically rolls back on teardown, preventing test data leakage into the database.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.pop(get_db, None)
