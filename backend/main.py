from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Women Safety App API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routes import sos, auth, tracking, checkin

app.include_router(sos.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(tracking.router, prefix="/api/tracking")
app.include_router(checkin.router, prefix="/api/checkin")

# Define path to frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# Serve API routes here
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Women Safety Backend is running"}

# Mount static files directly (JS, CSS)
app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
app.mount("/styles", StaticFiles(directory=os.path.join(frontend_dir, "styles")), name="styles")
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

# Serve the main frontend application
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    if full_path.startswith("api"):
        return {"error": "Endpoint not found"}
        
    requested_path = os.path.join(frontend_dir, full_path)
    if os.path.exists(requested_path) and os.path.isfile(requested_path):
        return FileResponse(requested_path)
        
    # Prevent serving index.html for static asset requests (e.g., .png, .ico, .json)
    if "." in os.path.basename(full_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")
        
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not built/found"}
