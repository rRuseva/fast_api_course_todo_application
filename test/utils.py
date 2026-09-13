import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..database import Base
from fastapi.testclient import TestClient
from ..main import app
from ..models import Todos, Users
from ..routers.auth import bcrypt_context


SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"id": 1, "username": "admin1", "role": "admin"}



@pytest.fixture
def create_todo():
    todo = Todos(title="Learn ot code!",
                 description="Need to learn everyday!",
                 priority=5,
                 complete=False,
                 owner_id = 1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()


@pytest.fixture
def create_admin_user():
    user = Users( 
        email = "admin@example.com",
        username = "admin1",
        first_name = "Admin",
        last_name = "User",
        hashed_password = bcrypt_context.hash("admin123"),
        role = "admin",
        phone_number = "359883250147",
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    
    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()
    
