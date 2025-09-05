from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.init_db import create_tables
from app.routers import tasks, auth
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    starlette_exception_handler,
)
import time
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup
    try:
        create_tables()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print(
            "Make sure PostgreSQL is running and connection details are correct in .env file"
        )

    yield

    # Shutdown
    print("Application shutting down...")


# Crear la instancia de FastAPI con configuración de producción
app = FastAPI(
    title="Taskify API",
    description="Una API REST para administrar tareas (TODOs) con autenticación JWT - Optimizada para producción",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Add CORS middleware for web frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
    ],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Add custom middleware for performance monitoring
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add response time header for monitoring"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f} seconds")
    return response


# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router)  # Authentication routes
app.include_router(tasks.router)  # Task management routes


# Health check endpoint for load balancers
@app.get("/health", tags=["monitoring"])
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    return {"status": "healthy", "timestamp": time.time(), "version": "1.0.0"}


# Root endpoint
@app.get("/", tags=["info"])
async def root():
    """API information endpoint"""
    return {
        "message": "Taskify API - Production Ready",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Para ejecutar con: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=1,  # For development. In production use: workers=4
    )
