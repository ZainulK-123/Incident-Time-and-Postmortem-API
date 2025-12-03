from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services import incident_service, timeline_service, postmortem_service

# Initialize FastAPI app
app = FastAPI(
    title="Incident Timeline and Postmortem API",
    description="API for managing incidents, timeline events, and postmortem reports",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://incident-time-and-postmortem-api-1.onrender.com"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include service routers
app.include_router(
    incident_service.router,
    prefix="/api/incidents",
    tags=["Incidents"]
)

app.include_router(
    timeline_service.router,
    prefix="/api/timeline",
    tags=["Timeline"]
)

app.include_router(
    postmortem_service.router,
    prefix="/api/postmortem",
    tags=["Postmortem"]
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with service information"""
    return {
        "message": "Welcome to Incident Timeline and Postmortem API",
        "version": "1.0.0",
        "services": {
            "incidents": "/api/incidents",
            "timeline": "/api/timeline",
            "postmortem": "/api/postmortem"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Incident Timeline and Postmortem API"
    }


