from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from MOD.models import User
from DB.database import get_db
from auth import hash_password, verify_password, create_token
from schemas import UserCreate, UserLogin

router = APIRouter()

@router.post("/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password, is_admin=user.is_admin)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user or not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user.email, existing_user.is_admin)
    return {"access_token": token, "token_type": "bearer"}
