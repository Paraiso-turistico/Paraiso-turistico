
import pytest

from domain.cliente import Cliente
from repository.cliente_repository import (
    ClienteRepository,
    ClienteDuplicadoError,
    RepositorioNoDisponibleError
)


# Crea un repositorio vacío para cada prueba.
@pytest.fixture
def repositorio():
    return ClienteRepository()


# Genera un cliente de prueba.
def crear_cliente(
    correo="carlos@example.com",
    documento="123456789"
):
    return Cliente(
        idUsuario=0,
        nombres="Carlos",
        apellidos="Ramirez",
        documento=documento,
        correo=correo,
        telefono="3001234567",
        contrasena_hash="hash_de_prueba"
    )


# Prueba el almacenamiento y la asignación del ID.
def test_guardar_cliente(repositorio):
    cliente = repositorio.guardar(crear_cliente())

    assert cliente.idUsuario == 101
    assert repositorio.existe_correo(cliente.correo)
    assert repositorio.existe_documento(cliente.documento)


# Prueba el rechazo de correos duplicados.
def test_correo_duplicado(repositorio):
    repositorio.guardar(crear_cliente())

    with pytest.raises(ClienteDuplicadoError):
        repositorio.guardar(
            crear_cliente(documento="987654321")
        )


# Prueba el rechazo de documentos duplicados.
def test_documento_duplicado(repositorio):
    repositorio.guardar(crear_cliente())

    with pytest.raises(ClienteDuplicadoError):
        repositorio.guardar(
            crear_cliente(correo="otro@example.com")
        )


# Prueba el rechazo de correos con distintas mayúsculas.
def test_correo_duplicado_mayusculas(repositorio):
    repositorio.guardar(crear_cliente())

    with pytest.raises(ClienteDuplicadoError):
        repositorio.guardar(
            crear_cliente(
                correo="CARLOS@example.com",
                documento="987654321"
            )
        )


# Prueba el comportamiento del repositorio no disponible.
def test_repositorio_no_disponible(repositorio):
    repositorio.disponible = False

    with pytest.raises(RepositorioNoDisponibleError):
        repositorio.guardar(crear_cliente())

    assert len(repositorio._clientes) == 0
    assert len(repositorio._notificaciones) == 0


# Prueba la generación de la solicitud de bienvenida.
def test_notificacion_bienvenida(repositorio):
    cliente = repositorio.guardar(crear_cliente())

    notificaciones = repositorio.obtener_notificaciones()

    assert len(notificaciones) == 1
    assert notificaciones[0].idUsuario == cliente.idUsuario
    assert notificaciones[0].correo == cliente.correo
    assert notificaciones[0].tipo == "BIENVENIDA"
    assert notificaciones[0].estado == "PENDIENTE"


# Comprueba que los duplicados no generen notificaciones.
def test_notificacion_duplicada(repositorio):
    repositorio.guardar(crear_cliente())

    with pytest.raises(ClienteDuplicadoError):
        repositorio.guardar(crear_cliente())

    assert len(repositorio._clientes) == 1
    assert len(repositorio.obtener_notificaciones()) == 1


# Simula un fallo al almacenar la notificación.
def test_reversion_registro(repositorio):

    class ListaConError(list):
        def append(self, elemento):
            raise RuntimeError("Fallo simulado")

    repositorio._notificaciones = ListaConError()

    with pytest.raises(RuntimeError):
        repositorio.guardar(crear_cliente())

    assert len(repositorio._clientes) == 0
    assert len(repositorio._notificaciones) == 0
    assert repositorio._siguiente_id == 101
