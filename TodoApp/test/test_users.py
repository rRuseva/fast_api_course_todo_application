from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status
import logging
from ..main import app

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(create_admin_user):
    response = client.get("/user/")
    logging.info(f"response: {response.json()}")
    logging.info(f"expected: {[(attr, val) for attr, val in create_admin_user.__dict__.items() if not attr.startswith('_')]}")
    assert response.status_code == status.HTTP_200_OK

    assert response.json().get("email") == create_admin_user.email
    assert response.json().get("username") == create_admin_user.username
    assert response.json().get("role") == create_admin_user.role
    assert response.json().get("first_name") == create_admin_user.first_name
    assert response.json().get("last_name") == create_admin_user.last_name
    assert response.json().get("phone_number") == create_admin_user.phone_number


def test_change_password_success(create_admin_user):
    new_password = "newtestpassword123"
    response = client.put(f"/user/user/{create_admin_user.id}", json={"password": "admin123", "new_password": new_password})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(create_admin_user):
    new_password = "newtestpassword123"
    response = client.put(f"/user/user/{create_admin_user.id}", json={"password": "wrongpassword", "new_password": new_password})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json().get("detail") == "Error on password change" 


def test_change_phone_number_success(create_admin_user):
    new_phone_number = "1234567890"
    response = client.put(f"/user/phonenumber/{new_phone_number}")
    assert response.status_code == status.HTTP_204_NO_CONTENT