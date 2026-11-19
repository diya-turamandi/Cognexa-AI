
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app import models
from app.routes import chat, sessions

from app.routes import documents


app = FastAPI(
    title="Cognexa AI",
    description="Your AI-powered personal knowledge management system",
    version="2.0.0"
)


@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(sessions.router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Cognexa AI",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "application": "Cognexa AI"
    }
