from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str