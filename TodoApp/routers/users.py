from typing import Annotated
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from ..models import Users, Todos
from ..database import SessionLocal
from .auth import get_current_user
from .routers_utils import redirect_to_login

templates = Jinja2Templates(directory="TodoApp/templates")


router = APIRouter(prefix="/user", tags=["user"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class UserRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str = Field(pattern=r"^(\+\d*)?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$")


### Pages ###
@router.get("/user-page/")
async def render_user_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

    except Exception as e:
        print(f"Exception: {e}")
        return redirect_to_login()

    try:
        user_data = db.query(Users).filter(Users.id == user.get("id")).first()
        return templates.TemplateResponse(
            name="user.html", request=request, context={"user_data": user_data, "user": user}
        )
    except Exception as e:
        print(f"Exception: {e}")


### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_user_data(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/password_change", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()


@router.put("/user/", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, user_request: UserRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail=f"User with the id {user.get('id')} is not available")

    for field, value in user_request.model_dump().items():
        print(f" Changing {field} to {value}")
        setattr(user_model, field, value)

    db.add(user_model)
    db.commit()
