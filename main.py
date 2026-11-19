from fastapi import FastAPI

app = FastAPI(
    title="API Paraíso Turístico",
    description="Servicios REST para la gestión turística",
    version="1.0.0"
)

@app.get("/")
def inicio():
    return {
        "mensaje": "API Paraíso Turístico funcionando",
        "success": True
    }