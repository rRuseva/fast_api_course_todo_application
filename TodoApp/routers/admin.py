from typing import Annotated, Literal
from fastapi import Depends, HTTPException, status, Path, APIRouter, Request
from sqlalchemy.orm import Session

from ..models import Todos, Users
from ..database import SessionLocal
from .auth import get_current_user
from ..schemas import TodoRequest, UserRequest, AdminUserRequest, AdminTodoRequest
from .routers_utils import redirect_to_login
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="TodoApp/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


### Pages ###
@router.get("/todos-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        entries = (
            db.query(Todos, Users.username, Users.id)
            .join(Users, Users.id == Todos.owner_id)
            .order_by(Users.id, Todos.id)
            .all()
        )
        todos_by_user = {}
        for todo, username, user_id in entries:
            todos_by_user.setdefault(
                user_id, {"username": username, "user_id": user_id, "todos": []}
            )["todos"].append(todo)

        return templates.TemplateResponse(
            name="admin-todos.html",
            request=request,
            context={"users_todos": list(todos_by_user.values()), "user": user},
        )
    except Exception as e:
        print(f"Exception: {e}")
        return redirect_to_login()


@router.get("/users-page")
async def render_users_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        users = (
            db.query(Users).all()
        )
        
        return templates.TemplateResponse(
            name="admin-users.html",
            request=request,
            context={"users": users, "user": user},
        )
    except Exception as e:
        print(f"Exception: {e}")
        return redirect_to_login()


@router.get("/edit-user-page/{user_id}")
async def render_edit_user_page(request: Request,
                                user_id: int,
                                db: db_dependency,
                            ):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

    except Exception as e:
        print(f"Exception: {e}")
        return redirect_to_login()

    try:
        user_data = db.query(Users).filter(Users.id == user_id).first()
        print(f"User data: {user_data}")
        return templates.TemplateResponse(
            name="user.html",
            request=request,
            context={"user_data": user_data, "user": user, "is_admin": True}
        )
    except Exception as e:
        print(f"Exception: {e}")


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request,
                                todo_id: int,
                                db: db_dependency,
                            ):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None or user.get("role") != "admin":
            return redirect_to_login()
    except Exception as e:
        print(f"Exception: {e}")
        return redirect_to_login()

    try:
        todo_data = db.query(Todos).filter(Todos.id == todo_id).first()
        print(f"Todo data: {todo_data}")
        return templates.TemplateResponse(
            name="edit-todo.html",
            request=request,
            context={"todo": todo_data, "user": user, "is_admin": True}
        )
    except Exception as e:
        print(f"Exception: {e}")


@router.get("/add-todo-page/{owner_id}")
async def render_add_todo_page(request: Request, owner_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None or user.get("role") != "admin":
            return redirect_to_login()

    except Exception as e:
        print(f"Exception: {e}")
        return redirect_to_login()

    try:
        return templates.TemplateResponse(
            name="add-todo.html",
            request=request,
            context={"user": user, "owner_id": owner_id, "is_admin": True}
        )
    except Exception as e:
        print(f"Exception: {e}")


## Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with the id {todo_id} is not available")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, todo_request: TodoRequest, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with the id {todo_id} is not available")
    for field, value in todo_request.dict().items():
        print(f" Changing {field} to {value}")
        setattr(todo_model, field, value)
    db.add(todo_model)
    db.commit()


@router.put("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user_id:int, user: user_dependency, user_admin_request: AdminUserRequest, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail=f"User with the id {user_id} is not available")

    for field, value in user_admin_request.model_dump().items():
        print(f" Changing {field} to {value}")
        setattr(user_model, field, value)

    db.add(user_model)
    db.commit()


@router.post("/todo/{owner_id}", status_code=status.HTTP_201_CREATED)
async def create_todo(owner_id:int,user: user_dependency, todo_request: TodoRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo_model = Todos(**todo_request.model_dump(), owner_id=owner_id)

    db.add(todo_model)
    db.commit()
