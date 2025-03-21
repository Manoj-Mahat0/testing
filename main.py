from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from DB.database import engine, Base
from routes import product, user, category, order
import os

app = FastAPI()

# ✅ Enable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

Base.metadata.create_all(bind=engine)

# ✅ Include Routers for APIs
app.include_router(user.router, prefix="/api")
app.include_router(product.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(order.router, prefix="/api")

# ✅ Serve React Frontend Build
if os.path.exists("web"):
    app.mount("/", StaticFiles(directory="web", html=True), name="frontend")

@app.get("/")
async def root():
    return {"message": "E-Commerce API is running"}
