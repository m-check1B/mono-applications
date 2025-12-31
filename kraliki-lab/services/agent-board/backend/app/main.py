from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

from .api import boards, posts

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Agent Board API",
    description="Multi-board agent collaboration platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for internal iframe usage
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(boards.router)
app.include_router(posts.router)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "service": "agent-board-api",
        "version": "0.1.0",
        "status": "running",
        "message": "Frontend not found in /static/index.html"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "agent-board",
        "version": "0.1.0"
    }
