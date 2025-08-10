"""
FastAPI Question Service - Main Entry Point

This is the main entry point for the FastAPI application.
Run this file to start the server.
"""

from app.__main__ import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.__main__:app", host="0.0.0.0", port=8000, reload=True)
