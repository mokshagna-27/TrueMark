from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analysis import router as analysis_router
from app.api.router import router as base_router
from app.api.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-assisted brand consistency platform "
        "for analyzing content against brand rules."
    ),
    debug=settings.DEBUG,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://true-mark-three.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# System endpoints: /health, /info, /features
app.include_router(
    base_router,
)

# Brand analysis endpoints: /api/v1/analysis/text
app.include_router(
    analysis_router,
    prefix=settings.API_PREFIX,
)


@app.get("/", tags=["System"])
def home():
    """Return a welcome message."""
    return {
        "message": "Welcome to TrueMark AI!",
        "status": "Backend is running",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
