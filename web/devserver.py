"""Local dev server: python devserver.py -> http://127.0.0.1:8000"""
import os
from app import app, PORT

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
