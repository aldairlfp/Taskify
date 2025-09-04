from fastapi import FastAPI

# Crear la instancia de FastAPI
app = FastAPI(
    title="Taskify API",
    description="Una API REST para administrar tareas (TODOs)",
    version="1.0.0",
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
