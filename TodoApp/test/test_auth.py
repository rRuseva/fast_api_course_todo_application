import pytest
from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, ALGORITHM, SECRET_KEY, get_current_user
from jose import jwt
from datetime import timedelta
from fastapi import HTTPException


app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(create_admin_user):
    db = TestingSessionLocal()

    non_existent_user = authenticate_user("nonexistentuser", "admin123", db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(create_admin_user.username, "wrongpassword", db)
    assert wrong_password_user is False
    
    authenticated_user = authenticate_user(create_admin_user.username,  "admin123", db)
    assert authenticated_user is not None
    assert authenticated_user.username == create_admin_user.username


def test_create_access_token():

    username = " testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})

    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role


@pytest.mark.asyncio
async def get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)
    assert user == {'user': 'testuser', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def get_current_user_missing_payload():

    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate user."
