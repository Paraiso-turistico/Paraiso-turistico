

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from domain.cliente import ClienteCreate
from domain.respuesta import RespuestaExitosa, RespuestaError

from repository.cliente_repository import (
    ClienteRepository,
    ClienteDuplicadoError,
    RepositorioNoDisponibleError
)

from service.cliente_service import ClienteService


# Repositorio y servicio compartidos por la aplicación.
repositorio = ClienteRepository()
servicio = ClienteService(repositorio)

# Define las rutas de autenticación.
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)


# Define el endpoint y documenta sus posibles respuestas HTTP.
@router.post(
    "/clientes",
    summary="Registrar cliente",
    description=(
        "Permite registrar un nuevo cliente en Paraíso Turístico. "
        "Valida los datos, verifica que el correo y documento sean únicos, "
        "protege la contraseña mediante hash, asigna automáticamente "
        "el rol CLIENTE y genera una solicitud de bienvenida pendiente."
    ),
    status_code=status.HTTP_201_CREATED,
    response_model=RespuestaExitosa,
    responses={
        400: {
            "model": RespuestaError,
            "description": "Datos inválidos o incompletos"
        },
        409: {
            "model": RespuestaError,
            "description": "Correo o documento duplicado"
        },
        503: {
            "model": RespuestaError,
            "description": "Servicio temporal no disponible"
        },
        500: {
            "model": RespuestaError,
            "description": "Error interno del servidor"
        }
    }
)
def registrar_cliente(datos: ClienteCreate):
    try:
        # Registra el cliente y devuelve sus datos públicos.
        cliente = servicio.registrar_cliente(datos)

        return {
            "mensaje": "Cliente registrado correctamente",
            "data": cliente,
            "success": True
        }

    except ClienteDuplicadoError:
        # Error por correo o documento duplicado.
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": "El correo o documento ya se encuentra registrado",
                "data": None,
                "success": False
            }
        )

    except RepositorioNoDisponibleError:
        # Error por falta de disponibilidad del repositorio.
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "mensaje": "Servicio temporal no disponible. Intente nuevamente más tarde.",
                "data": None,
                "success": False
            }
        )

    except Exception:
        # Controla errores inesperados sin exponer información interna.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "mensaje": "Ha ocurrido un error interno en el servidor",
                "data": None,
                "success": False
            }
        )
