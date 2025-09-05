from fastapi import FastAPI
from app.core.init_db import create_tables
from app.routers import tasks, auth

# Crear la instancia de FastAPI
app = FastAPI(
    title="Taskify API",
    description="Una API REST para administrar tareas (TODOs) con autenticación JWT",
    version="1.0.0",
)

# Include routers
app.include_router(auth.router)  # Authentication routes
app.include_router(tasks.router)  # Task management routes


# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables when the application starts"""
    try:
        create_tables()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print(
            "Make sure PostgreSQL is running and connection details are correct in .env file"
        )


# Ruta básica de prueba
@app.get("/")
async def root():
    return {"message": "¡Bienvenido a Taskify API!"}


# Ruta de health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Taskify API"}


# Para ejecutar con: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
