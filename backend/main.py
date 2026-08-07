import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.database import init_cache, close_cache, get_cache, supabase
from app.rate_limiter import limiter
from app.routers import auth, speech, conversation, interview, tutor, group, progress
from app.routers import credential

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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS - explicit allowlist. `allow_origins=["*"]` + `allow_credentials=True` is
# an invalid combination (browsers reject/strip credentials on wildcard origins)
# and would otherwise let any site make authenticated requests on a user's behalf.
_allowed_origins = [settings.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Assigns a request ID and logs method/path/status/latency for every request."""
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.error(f"[{request_id}] {request.method} {request.url.path} -> 500 ({duration_ms}ms)")
        raise
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    return response


# Routers
app.include_router(auth.router)
app.include_router(speech.router)
app.include_router(conversation.router)
app.include_router(interview.router)
app.include_router(tutor.router)
app.include_router(group.router)
app.include_router(progress.router)
app.include_router(credential.router)

@app.get("/")
async def root():
    return {"message": "Vani API is running", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Liveness + dependency check, suitable for a load balancer/k8s probe."""
    checks = {"database": "ok", "cache": "ok"}
    healthy = True

    try:
        await supabase.table("users").select("id").limit(1).execute()
    except Exception as e:
        checks["database"] = f"error: {e}"
        healthy = False

    try:
        cache = await get_cache()
        await cache.ping()
    except Exception as e:
        checks["cache"] = f"error: {e}"
        healthy = False

    status_code = 200 if healthy else 503
    return JSONResponse(status_code=status_code, content={"status": "ok" if healthy else "degraded", "checks": checks})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)