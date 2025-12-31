#!/usr/bin/env python3
"""
Start the backend server and ensure database tables exist.
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_tables():
    """Create all database tables."""
    from app.database import Base, engine
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"Warning: Could not create tables: {e}")
        print("The application will try to run anyway...")

def main():
    """Main entry point."""
    # Create tables first
    create_tables()
    
    # Start the server
    import uvicorn
    from app.main import app
    
    print("Starting FastAPI server on 0.0.0.0:8000...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # Disable reload in production
    )

if __name__ == "__main__":
    main()
