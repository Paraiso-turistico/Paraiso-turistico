
import pytest
from fastapi.testclient import TestClient

from main import app
from api import cliente_router
from repository.cliente_repository import ClienteRepository
from service.cliente_service import ClienteService


RUTA = "/api/v1/auth/clientes"


# Prepara un entorno independiente para cada prueba.
@pytest.fixture
def entorno(monkeypatch):
    repositorio = ClienteRepository()
    servicio = ClienteService(repositorio)

    monkeypatch.setattr(cliente_router, "repositorio", repositorio)
    monkeypatch.setattr(cliente_router, "servicio", servicio)

    return TestClient(app), repositorio


# Genera un JSON válido para registrar clientes.
def crear_datos():
    return {
        "nombres": "Carlos",
        "apellidos": "Ramirez",
        "documento": "123456789",
        "correo": "carlos@example.com",
        "telefono": "3001234567",
        "contrasena": "ClavePrueba2026!"
    }


# Comprueba el registro exitoso y el contrato de respuesta.
def test_registro_exitoso(entorno):
    cliente, repositorio = entorno

    respuesta = cliente.post(RUTA, json=crear_datos())

    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "mensaje": "Cliente registrado correctamente",
        "data": {
            "idUsuario": 101,
            "nombres": "Carlos",
            "rol": "CLIENTE",
            "estado": "ACTIVO"
        },
        "success": True
    }


# Comprueba el rechazo de correos duplicados.
def test_correo_duplicado(entorno):
    cliente, repositorio = entorno

    cliente.post(RUTA, json=crear_datos())

    datos = crear_datos()
    datos["documento"] = "987654321"

    respuesta = cliente.post(RUTA, json=datos)

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "mensaje": "El correo o documento ya se encuentra registrado",
        "data": None,
        "success": False
    }


# Comprueba el rechazo de documentos duplicados.
def test_documento_duplicado(entorno):
    cliente, repositorio = entorno

    cliente.post(RUTA, json=crear_datos())

    datos = crear_datos()
    datos["correo"] = "otro@example.com"

    respuesta = cliente.post(RUTA, json=datos)

    assert respuesta.status_code == 409


# Comprueba la validación del correo electrónico.
def test_correo_invalido(entorno):
    cliente, repositorio = entorno

    datos = crear_datos()
    datos["correo"] = "correo-invalido"

    respuesta = cliente.post(RUTA, json=datos)

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "mensaje": "Los datos enviados son inválidos o incompletos",
        "data": None,
        "success": False
    }

    assert len(repositorio._clientes) == 0


# Comprueba el rechazo de campos obligatorios faltantes.
def test_campo_faltante(entorno):
    cliente, repositorio = entorno

    datos = crear_datos()
    del datos["contrasena"]

    respuesta = cliente.post(RUTA, json=datos)

    assert respuesta.status_code == 400
    assert len(repositorio._clientes) == 0


# Comprueba el rechazo de tipos de datos incorrectos.
def test_tipo_incorrecto(entorno):
    cliente, repositorio = entorno

    datos = crear_datos()
    datos["documento"] = 123456789

    respuesta = cliente.post(RUTA, json=datos)

    assert respuesta.status_code == 400


# Comprueba que no se puedan asignar roles no autorizados.
@pytest.mark.parametrize("rol", ["ADMINISTRADOR", "PROVEEDOR"])
def test_rol_no_autorizado(entorno, rol):
    cliente, repositorio = entorno

    datos = crear_datos()
    datos["rol"] = rol

    respuesta = cliente.post(RUTA, json=datos)

    assert respuesta.status_code == 400
    assert len(repositorio._clientes) == 0


# Comprueba la ausencia de datos sensibles.
def test_respuesta_segura(entorno):
    cliente, repositorio = entorno

    respuesta = cliente.post(RUTA, json=crear_datos())

    assert respuesta.status_code == 201
    assert "contrasena" not in respuesta.text
    assert "ClavePrueba2026!" not in respuesta.text
    assert repositorio._clientes[101].contrasena_hash not in respuesta.text


# Comprueba el código 503 cuando falla el repositorio.
def test_servicio_no_disponible(entorno):
    cliente, repositorio = entorno

    repositorio.disponible = False

    respuesta = cliente.post(RUTA, json=crear_datos())

    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "mensaje": "Servicio temporal no disponible. Intente nuevamente más tarde.",
        "data": None,
        "success": False
    }

    assert len(repositorio._clientes) == 0
    assert len(repositorio._notificaciones) == 0


# Simula un error inesperado del servicio.
def test_error_interno(entorno, monkeypatch):
    cliente, repositorio = entorno

    def generar_error(datos):
        raise RuntimeError("Error interno simulado")

    monkeypatch.setattr(
        cliente_router.servicio,
        "registrar_cliente",
        generar_error
    )

    respuesta = cliente.post(RUTA, json=crear_datos())

    assert respuesta.status_code == 500
    assert respuesta.json() == {
        "mensaje": "Ha ocurrido un error interno en el servidor",
        "data": None,
        "success": False
    }

    assert len(repositorio._clientes) == 0


# Comprueba los códigos documentados en OpenAPI.
def test_documentacion_openapi(entorno):
    cliente, repositorio = entorno

    respuesta = cliente.get("/openapi.json")

    assert respuesta.status_code == 200

    respuestas = respuesta.json()["paths"][RUTA]["post"]["responses"]

    assert set(respuestas.keys()) == {
        "201", "400", "409", "500", "503"
    }
