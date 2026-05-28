from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.database import init_cache, close_cache
from app.routers import auth, speech, conversation, interview, tutor, group, progress

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Vani backend...")
    await init_cache()
    yield
    await close_cache()
    logger.info("Shutting down...")

app = FastAPI(
    title="Vani API",
    description="AI Communication Coach for First-Gen Learners",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(speech.router)
app.include_router(conversation.router)
app.include_router(interview.router)
app.include_router(tutor.router)
app.include_router(group.router)
app.include_router(progress.router)

@app.get("/")
async def root():
    return {"message": "Vani API is running", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}