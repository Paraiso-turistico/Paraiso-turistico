
import pytest

from domain.cliente import ClienteCreate
from repository.cliente_repository import (
    ClienteRepository,
    ClienteDuplicadoError,
    RepositorioNoDisponibleError
)
from service.cliente_service import ClienteService


# Prepara un repositorio y servicio independientes para cada prueba.
@pytest.fixture
def entorno():
    repositorio = ClienteRepository()
    servicio = ClienteService(repositorio)

    return repositorio, servicio


# Genera datos válidos para registrar clientes.
def crear_datos(
    correo="carlos@example.com",
    documento="123456789"
):
    return ClienteCreate(
        nombres="Carlos",
        apellidos="Ramirez",
        documento=documento,
        correo=correo,
        telefono="3001234567",
        contrasena="ClavePrueba2026!"
    )


# Comprueba el registro exitoso.
def test_registro_exitoso(entorno):
    repositorio, servicio = entorno

    resultado = servicio.registrar_cliente(crear_datos())

    assert resultado["idUsuario"] == 101
    assert resultado["nombres"] == "Carlos"
    assert resultado["rol"] == "CLIENTE"
    assert resultado["estado"] == "ACTIVO"


# Comprueba que la contraseña se almacene mediante hash.
def test_contrasena_protegida(entorno):
    repositorio, servicio = entorno

    datos = crear_datos()
    servicio.registrar_cliente(datos)

    cliente = repositorio._clientes[101]

    assert cliente.contrasena_hash != datos.contrasena
    assert cliente.contrasena_hash.startswith("scrypt$")


# Comprueba que contraseñas iguales generen hashes diferentes.
def test_hashes_diferentes(entorno):
    repositorio, servicio = entorno

    servicio.registrar_cliente(crear_datos())

    servicio.registrar_cliente(
        crear_datos(
            correo="otro@example.com",
            documento="987654321"
        )
    )

    cliente1 = repositorio._clientes[101]
    cliente2 = repositorio._clientes[102]

    assert cliente1.contrasena_hash != cliente2.contrasena_hash


# Comprueba que la respuesta solo incluya datos públicos.
def test_respuesta_sin_datos_sensibles(entorno):
    repositorio, servicio = entorno

    resultado = servicio.registrar_cliente(crear_datos())

    assert set(resultado.keys()) == {
        "idUsuario",
        "nombres",
        "rol",
        "estado"
    }


# Comprueba el rechazo de correos duplicados.
def test_correo_duplicado(entorno):
    repositorio, servicio = entorno

    servicio.registrar_cliente(crear_datos())

    with pytest.raises(ClienteDuplicadoError):
        servicio.registrar_cliente(
            crear_datos(documento="987654321")
        )


# Comprueba el rechazo de documentos duplicados.
def test_documento_duplicado(entorno):
    repositorio, servicio = entorno

    servicio.registrar_cliente(crear_datos())

    with pytest.raises(ClienteDuplicadoError):
        servicio.registrar_cliente(
            crear_datos(correo="otro@example.com")
        )


# Comprueba el comportamiento ante un repositorio no disponible.
def test_servicio_no_disponible(entorno):
    repositorio, servicio = entorno

    repositorio.disponible = False

    with pytest.raises(RepositorioNoDisponibleError):
        servicio.registrar_cliente(crear_datos())

    assert len(repositorio._clientes) == 0
    assert len(repositorio._notificaciones) == 0


# Comprueba la generación de la notificación de bienvenida.
def test_generar_notificacion(entorno):
    repositorio, servicio = entorno

    resultado = servicio.registrar_cliente(crear_datos())

    notificaciones = repositorio.obtener_notificaciones()

    assert len(notificaciones) == 1
    assert notificaciones[0].idUsuario == resultado["idUsuario"]
    assert notificaciones[0].estado == "PENDIENTE"
