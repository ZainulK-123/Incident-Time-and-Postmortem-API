from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, incidents, timeline, postmortem

app = FastAPI(title="Incident Management API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Incident Management API"}

# We will include routers here later
app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(timeline.router)
app.include_router(postmortem.router)
