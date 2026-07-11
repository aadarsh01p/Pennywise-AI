from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.pages import router as pages_router
from app.routes.transactions import router as transaction_router
from app.models.password_reset import PasswordReset
from app.routes.dashboard import router as dashboard_router
from app.routes.upload import router as upload_router
# ==========================================
# Create Database Tables
# ==========================================
Base.metadata.create_all(bind=engine)

# ==========================================
# FastAPI Application
# ==========================================
app = FastAPI(
    title="PennyWise AI",
    version="1.0.0"
)

# ==========================================
# CORS Configuration
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Static Files
# ==========================================
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# ==========================================
# Routers
# ==========================================
app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(transaction_router)
app.include_router(dashboard_router)
app.include_router(upload_router)

# ==========================================
# Health Check
# ==========================================
@app.get("/api")
def api():
    return {
        "message": "PennyWise AI Backend Running 🚀"
    }
