import hashlib
import secrets

from domain.cliente import Cliente, ClienteCreate
from repository.cliente_repository import (
    ClienteRepository,
    ClienteDuplicadoError,
    RepositorioNoDisponibleError
)


class ClienteService:

    def __init__(self, repositorio: ClienteRepository):
        self.repositorio = repositorio

    def _generar_hash(self, contrasena: str) -> str:
        # Genera una sal aleatoria para proteger la contraseña.
        salt = secrets.token_bytes(16)

        # Convierte la contraseña en un hash seguro.
        hash_contrasena = hashlib.scrypt(
            contrasena.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=64
        )

        return f"scrypt${salt.hex()}${hash_contrasena.hex()}"

    def registrar_cliente(self, datos: ClienteCreate) -> dict:
        # Comprueba que el correo y el documento no estén registrados.
        if self.repositorio.existe_correo(datos.correo):
            raise ClienteDuplicadoError()

        if self.repositorio.existe_documento(datos.documento):
            raise ClienteDuplicadoError()

        # Protege la contraseña antes de guardar al cliente.
        contrasena_hash = self._generar_hash(datos.contrasena)

        # Crea el cliente con rol y estado definidos por el dominio.
        nuevo_cliente = Cliente(
            idUsuario=0,
            nombres=datos.nombres,
            apellidos=datos.apellidos,
            documento=datos.documento,
            correo=datos.correo,
            telefono=datos.telefono,
            contrasena_hash=contrasena_hash
        )

        # Guarda el cliente y devuelve únicamente sus datos públicos.
        cliente_guardado = self.repositorio.guardar(nuevo_cliente)

        return cliente_guardado.to_response()