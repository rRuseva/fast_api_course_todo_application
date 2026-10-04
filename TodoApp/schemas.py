from typing import Annotated, Literal
from pydantic import BaseModel, Field

class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=200)
    priority: int = Field(gt=0, lt=6)
    complete: bool = Field(default=False)


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class UserRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str = Field(pattern=r"^(\+\d*)?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$")


class AdminUserRequest(UserRequest):
    role: Literal["user", "admin"] = Field(default="user")
    username:str = Field(min_length=3, max_length=50)