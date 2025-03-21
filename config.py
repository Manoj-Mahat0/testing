import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env file (if exists)
load_dotenv()

# ✅ Assign necessary values with a fallback
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://freedb_manoj:ZscbxA%8!BK!7qV@sql.freedb.tech:3306/freedb_ecom_db")
SECRET_KEY = os.getenv("SECRET_KEY", "manoj")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# ✅ Raise an error if DATABASE_URL is missing
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set. Check your .env file or Render settings!")

