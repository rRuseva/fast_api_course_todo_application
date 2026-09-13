from ..routers.admin import get_db, get_current_user
from fastapi import status
import logging
from ..main import app
from ..models import Users, Todos
from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(create_todo):
    response = client.get("/admin/")
    
    assert response.status_code == status.HTTP_200_OK
    expected_todos = [{"title": create_todo.title,
                                "description": create_todo.description,
                                "priority": create_todo.priority,
                                "complete": create_todo.complete,
                                "owner_id": create_todo.owner_id,   
                                "id": create_todo.id}]
    logging.info(f"expected todos: {expected_todos}")
    logging.info(f"response todos: {response.json()}")
    assert response.json() == expected_todos


def test_admin_delete_todo(create_todo):
    response = client.delete(f"/admin/todo/{create_todo.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Verify that the todo is deleted from the database
    db = TestingSessionLocal()
    deleted_todo = db.query(Todos).filter(Todos.id == create_todo.id).first()
    assert deleted_todo is None


def test_admin_delete_todo_not_found(create_todo):
    non_existent_todo_id = 9999  # Assuming this ID does not exist
    response = client.delete(f"/admin/todo/{non_existent_todo_id}")  # Assuming 9999 is a non-existent todo ID
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {f"detail": f"Todo with the id {non_existent_todo_id} is not available"}