"""
InboxPilot API Server
Refactored FastAPI server with modular routes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import route modules
from api.routes import emails_router, actions_router, scheduler_router

app = FastAPI(
    title="InboxPilot API",
    description="Automated Android Email Triage & Decision Dashboard",
    version="2.0.0"
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(emails_router)
app.include_router(actions_router)
app.include_router(scheduler_router)


@app.get("/")
def read_root():
    return {
        "message": "InboxPilot API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "emails": "/api/emails",
            "scan_inbox": "/api/emails/scan",
            "recategorize": "/api/emails/recategorize",
            "actions": "/api/actions",
            "scheduler": "/api/scheduler/run",
            "stats": "/api/stats"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "inboxpilot-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
