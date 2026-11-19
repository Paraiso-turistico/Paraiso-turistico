from threading import Lock
from domain.cliente import Cliente


class ClienteDuplicadoError(Exception):
    pass


class RepositorioNoDisponibleError(Exception):
    pass


class ClienteRepository:

    def __init__(self):
        self._clientes: dict[int, Cliente] = {}
        self._siguiente_id = 101
        self._lock = Lock()
        self.disponible = True

    def _verificar_disponibilidad(self):
        if not self.disponible:
            raise RepositorioNoDisponibleError()

    def existe_correo(self, correo: str) -> bool:
        with self._lock:
            self._verificar_disponibilidad()

            return any(
                cliente.correo.casefold() == correo.casefold()
                for cliente in self._clientes.values()
            )

    def existe_documento(self, documento: str) -> bool:
        with self._lock:
            self._verificar_disponibilidad()

            return any(
                cliente.documento == documento
                for cliente in self._clientes.values()
            )

    def guardar(self, cliente: Cliente) -> Cliente:
        with self._lock:
            self._verificar_disponibilidad()

            for registrado in self._clientes.values():
                if (
                    registrado.correo.casefold() == cliente.correo.casefold()
                    or registrado.documento == cliente.documento
                ):
                    raise ClienteDuplicadoError()

            cliente.idUsuario = self._siguiente_id
            self._clientes[cliente.idUsuario] = cliente
            self._siguiente_id += 1

            return cliente