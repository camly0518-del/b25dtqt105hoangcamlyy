import os
import sys

# Thêm thư mục gốc vào sys.path để import được app
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app

# Vercel Serverless Function entrypoint
# Đối tượng app (FastAPI ASGI) sẽ được Vercel tự động xử lý
