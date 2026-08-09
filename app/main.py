from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from app.database import Base, engine
from app.routes.auth import router as auth_router
from app.routes.pages import router as pages_router
from app.routes.transactions import router as transaction_router
from app.routes.dashboard import router as dashboard_router
from app.routes.upload import router as upload_router
from app.routes.reports import router as reports_router
from app.routes import budget
from app.routes.goals import router as goals_router
from app.routes.chatbot import router as chatbot_router
from app.models.password_reset import PasswordReset

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
# Chatbot Page
# ==========================================
@app.get("/chatbot")
async def chatbot_page():
    return FileResponse(
        "app/templates/chatbot.html"
    )

# ==========================================
# Routers
# ==========================================
app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(transaction_router)
app.include_router(dashboard_router)
app.include_router(upload_router)
app.include_router(reports_router)
app.include_router(budget.router)
app.include_router(goals_router)
app.include_router(chatbot_router)

@app.get("/api")
def api():
    return {
        "message": "PennyWise AI Backend Running 🚀"
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.ico")

@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
async def chrome_devtools():
    return Response(status_code=204)