from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from MOD.models import Product, Category
from DB.database import get_db
from auth import get_current_user

router = APIRouter()

# Define request models
class ProductRequest(BaseModel):
    name: str
    category_name: str
    price: float
    stock: int
    token: str  # Token required

class ProductUpdateRequest(BaseModel):
    name: str  # Identify product by name
    category_name: str
    price: float
    stock: int
    token: str

class DeleteProductRequest(BaseModel):
    id: int
    token: str  # Token required


# 🟢 **Add Product**
@router.post("/product/add")
async def add_product(request: ProductRequest, db: Session = Depends(get_db)):
    user = get_current_user(request.token)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can add products")

    # Check if category exists; otherwise, create it
    category = db.query(Category).filter(Category.name == request.category_name).first()
    if not category:
        category = Category(name=request.category_name)
        db.add(category)
        db.commit()
        db.refresh(category)

    # Check if a product with the same name exists in the same category
    existing_product = db.query(Product).filter(
        Product.name == request.name, 
        Product.category_id == category.id
    ).first()

    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists in this category")

    # Create and save new product
    new_product = Product(
        name=request.name,
        category_id=category.id,
        price=request.price,
        stock=request.stock
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Product added successfully", "product_name": new_product.name}


# 🟡 **Edit Product**
@router.put("/product/update")
async def update_product(request: ProductUpdateRequest, db: Session = Depends(get_db)):
    print("🔹 Received Update Request:", request.dict())  # ✅ Debugging

    user = get_current_user(request.token)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can update products")

    # 🔍 Find the product by name
    product = db.query(Product).filter(Product.name == request.name).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 🔄 Handle category update
    if request.category_name:
        category = db.query(Category).filter(Category.name == request.category_name).first()
        if not category:
            category = Category(name=request.category_name)
            db.add(category)
            db.commit()
            db.refresh(category)

        product.category_id = category.id  # ✅ Update category_id in product

    # 🔄 Update price and stock
    product.price = request.price
    product.stock = request.stock

    db.commit()
    db.refresh(product)

    return {"message": "Product updated successfully", "product_name": product.name, "category": category.name}


# 🔴 **Delete Product**
@router.delete("/product/delete")
async def delete_product(request: DeleteProductRequest, db: Session = Depends(get_db)):
    user = get_current_user(request.token)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can delete products")

    # Find the product by ID
    product = db.query(Product).filter(Product.id == request.id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}

# 🟢 **Get All Products**
@router.get("/products")
async def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).join(Category).all()
    result = [
        {
            "id": product.id,
            "name": product.name,
            "category": product.category.name,  # Fetch category name instead of ID
            "price": product.price,
            "stock": product.stock
        }
        for product in products
    ]
    return result
