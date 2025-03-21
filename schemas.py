from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: Optional[bool] = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ProductCreate(BaseModel):
    name: str
    category_name: str
    price: float
    stock: int

class OrderCreate(BaseModel):
    product_id: int
    user_email: EmailStr
    quantity: int
