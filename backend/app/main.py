
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import documents


app = FastAPI(
    title="Cognexa AI",
    description="Your AI-powered personal knowledge management system",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(documents.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Cognexa AI Backend",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "application": "Cognexa AI"
    }
