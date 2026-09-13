from ..routers.todos import get_db, get_current_user
from fastapi import status
import logging
from ..main import app
from ..models import Todos
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(create_todo):
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    logging.info(f"Response JSON: {response.json()}")
    expected_todo = [{"title": create_todo.title,
                                "description": create_todo.description,
                                "priority": create_todo.priority,
                                "complete": create_todo.complete,
                                "owner_id": create_todo.owner_id,   
                                "id": create_todo.id}]
    logging.info(f"Expected: {expected_todo}")
    logging.info(response.json() == expected_todo)
    assert response.json() == expected_todo


def test_read_one_authenticated(create_todo):
    response = client.get("/todo/1")

    assert response.status_code == status.HTTP_200_OK
    logging.info(f"Response JSON: {response.json()}")
    expected_todo = {"title": create_todo.title,
                    "description": create_todo.description,
                    "priority": create_todo.priority,
                    "complete": create_todo.complete,
                    "owner_id": create_todo.owner_id,   
                    "id": create_todo.id}
    logging.info(f"Expected: {expected_todo}")
    logging.info(response.json() == expected_todo)
    assert response.json() == expected_todo



def test_read_one_authenticated_not_found(create_todo):
    wanted_id = 999
    response = client.get(f"/todo/{wanted_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Todo with the id {wanted_id} is not available"}


def test_create_todo(create_todo):
    new_todo = {"title": "New TODO",
                "description":  "New TODO description",
                "priority": 5,
                "complete": False
                }
    response = client.post('/todo/',json=new_todo)

    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == new_todo.get('title')
    assert model.description == new_todo.get('description')
    assert model.priority == new_todo.get('priority')
    assert model.complete == new_todo.get('complete')


def test_update_todo(create_todo):
    logging.info(f"Created TODO: {create_todo.title}")
    request_data = {
        'title': "Updated todo title",
        'description': create_todo.description,
        'priority': create_todo.priority,
        'complete': create_todo.complete
    }

    response = client.put(f"/todo/{create_todo.id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == create_todo.id).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo_not_found(create_todo):
    logging.info(f"Created TODO: {create_todo.title}")
    request_data = {
        'title': "Updated todo title",
        'description': create_todo.description,
        'priority': create_todo.priority,
        'complete': create_todo.complete
    }
    not_existing_id = 999
    response = client.put(f"/todo/{not_existing_id}", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Todo with the id {not_existing_id} is not available"}


def test_delete_todo(create_todo):
    response = client.delete(f"/todo/{create_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == create_todo.id).first()
    assert model is None


def test_delete_todo_not_found():
    non_existing_id = 999
    response = client.delete(f"/todo/{non_existing_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Todo with the id {non_existing_id} is not available"}