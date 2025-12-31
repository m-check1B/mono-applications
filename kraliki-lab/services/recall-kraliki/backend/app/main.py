"""
recall-kraliki FastAPI Backend
Persistent knowledge system with GLM 4.6 semantic search
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="recall-kraliki API",
    description="Persistent knowledge system with hybrid search",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5176", "http://127.0.0.1:5176"],  # Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "recall-kraliki",
        "version": "0.1.0"
    }

# Root
@app.get("/")
async def root():
    """API root"""
    return {
        "message": "recall-kraliki API",
        "docs": "/docs",
        "health": "/health"
    }

# Import routers
from .api import search, capture, graph, stats, entries

app.include_router(capture.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(entries.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=3020,
        reload=True
    )
