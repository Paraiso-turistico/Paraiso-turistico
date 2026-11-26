

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from api.cliente_router import router as cliente_router


# Configuración principal de la API.
app = FastAPI(
    title="API Paraíso Turístico",
    description="Servicios REST para la gestión turística",
    version="1.0.0"
)

# Registra las rutas del módulo de clientes.
app.include_router(cliente_router)


# Convierte los errores de validación en respuestas HTTP 400.
@app.exception_handler(RequestValidationError)
async def error_validacion(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "mensaje": "Los datos enviados son inválidos o incompletos",
            "data": None,
            "success": False
        }
    )


# Personaliza la documentación OpenAPI.
def personalizar_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    esquema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )

    # Elimina el código 422 del endpoint de registro.
    esquema["paths"]["/api/v1/auth/clientes"]["post"][
        "responses"
    ].pop("422", None)

    app.openapi_schema = esquema

    return esquema


# Aplica la documentación personalizada.
app.openapi = personalizar_openapi


# Ruta para comprobar el funcionamiento de la API.
@app.get("/")
def inicio():
    return {
        "mensaje": "API Paraíso Turístico funcionando",
        "success": True
    }
