from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from MOD.models import Category
from DB.database import get_db
from auth import get_current_user

router = APIRouter()

# 📌 Request Models
class CategoryRequest(BaseModel):
    name: str
    token: str  # For admin authentication

class CategoryUpdateRequest(BaseModel):
    old_name: str
    new_name: str
    token: str

class DeleteCategoryRequest(BaseModel):
    name: str
    token: str

# 🟢 **Add Category**
@router.post("/category/add")
async def add_category(request: CategoryRequest, db: Session = Depends(get_db)):
    user = get_current_user(request.token)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can add categories")

    # Check if category already exists
    existing_category = db.query(Category).filter(Category.name == request.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(name=request.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {"message": "Category added successfully", "category": new_category.name}

# 🟡 **Update Category (Rename)**
@router.put("/category/update")
async def update_category(request: CategoryUpdateRequest, db: Session = Depends(get_db)):
    user = get_current_user(request.token)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can update categories")

    category = db.query(Category).filter(Category.name == request.old_name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = request.new_name  # Update category name
    db.commit()
    db.refresh(category)

    return {"message": "Category updated successfully", "new_name": category.name}

# 🔴 **Delete Category**
@router.delete("/category/delete")
async def delete_category(request: DeleteCategoryRequest, db: Session = Depends(get_db)):
    user = get_current_user(request.token)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can delete categories")

    category = db.query(Category).filter(Category.name == request.name).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}

# 🔵 **Get All Categories**
@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [{"id": category.id, "name": category.name} for category in categories]
