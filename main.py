import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import engine, Base
from seed import init_db_and_seed

# Routers
from routers import auth, pengumuman, pengurus, forms, upload, stats, dynamic_forms

# Create tables on startup
Base.metadata.create_all(bind=engine)
init_db_and_seed()

app = FastAPI(
    title="PMK Daniel API",
    description="Backend REST API untuk Website Resmi PMK Daniel FILKOM Universitas Brawijaya",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Mount local uploads directory if it exists
os.makedirs("./uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(pengumuman.router)
app.include_router(pengurus.router)
app.include_router(forms.router)
app.include_router(dynamic_forms.router)
app.include_router(upload.router)
app.include_router(stats.router)

# Root / Health check
@app.get("/", tags=["Health Check"])
def root():
    return {
        "success": True,
        "service": "PMK Daniel Python FastAPI",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

# Global Custom Exception Handlers for standard JSON response envelope
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "message": str(exc.detail)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = errors[0]["msg"] if errors else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "message": f"{error_msg} ({errors[0].get('loc', [''])[ -1]})" if errors else error_msg,
            "details": errors
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
