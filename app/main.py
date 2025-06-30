from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.endpoints import router

app = FastAPI(
    title="Natural Language SQL Tool",
    description="Convert natural language queries to PostgreSQL",
    version="1.0.0"
)

# Include API routes
app.include_router(router)

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main web interface"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Natural Language SQL Tool API"} 