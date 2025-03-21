from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from MOD.models import Product, Order
from DB.database import get_db
from auth import get_current_user

router = APIRouter()

# 🟢 **Order Request Model**
class OrderRequest(BaseModel):
    product_name: str
    quantity: int


class AcceptOrderRequest(BaseModel):
    order_id: int
    token: str  # Admin token

# 🛍 **User Places an Order**
@router.post("/order/place")
async def place_order(request: OrderRequest, db: Session = Depends(get_db)):
    try:
        # ✅ Find the product
        product = db.query(Product).filter(Product.name == request.product_name).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{request.product_name}' not found")

        # ✅ Validate stock
        if request.quantity > product.stock:
            raise HTTPException(status_code=400, detail="Not enough stock available")

        # ✅ Create and save order without user_id
        new_order = Order(
            product_id=product.id,
            quantity=request.quantity,
            status="Pending"
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return {"message": "Order placed successfully", "order_id": new_order.id}

    except Exception as e:
        db.rollback()  # Rollback on failure
        raise HTTPException(status_code=500, detail=str(e))  # Log actual error

# 🟡 **Admin Accepts Order (Stock Decreases)**
@router.put("/order/accept")
async def accept_order(request: AcceptOrderRequest, db: Session = Depends(get_db)):
    user = get_current_user(request.token)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can accept orders")

    order = db.query(Order).filter(Order.id == request.order_id, Order.status == "Pending").first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or already processed")

    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if order.quantity > product.stock:
        raise HTTPException(status_code=400, detail="Not enough stock to fulfill this order")

    # ✅ Accept order and decrease stock
    order.status = "Accepted"
    product.stock -= order.quantity

    db.commit()
    return {"message": "Order accepted, stock updated", "remaining_stock": product.stock}

# 📜 **List All Orders (Admin Only)**
@router.get("/orders")
async def list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    result = [
        {
            "id": order.id,
            "product_name": order.product.name,  # ✅ Now this works!
            "quantity": order.quantity,
            "status": order.status
        }
        for order in orders
    ]
    return result
