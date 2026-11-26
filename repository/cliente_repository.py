
from threading import Lock

from domain.cliente import Cliente
from domain.notificacion import Notificacion


# Error por correo o documento duplicado.
class ClienteDuplicadoError(Exception):
    pass


# Error por falta de disponibilidad del repositorio.
class RepositorioNoDisponibleError(Exception):
    pass


class ClienteRepository:

    def __init__(self):
        # Almacena clientes y notificaciones en memoria.
        self._clientes: dict[int, Cliente] = {}
        self._notificaciones: list[Notificacion] = []

        self._siguiente_id = 101
        self._lock = Lock()
        self.disponible = True

    def _verificar_disponibilidad(self):
        if not self.disponible:
            raise RepositorioNoDisponibleError()

    def existe_correo(self, correo: str) -> bool:
        with self._lock:
            self._verificar_disponibilidad()

            # Compara correos sin distinguir mayúsculas y minúsculas.
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

            # Verifica nuevamente los posibles duplicados.
            for registrado in self._clientes.values():
                if (
                    registrado.correo.casefold() == cliente.correo.casefold()
                    or registrado.documento == cliente.documento
                ):
                    raise ClienteDuplicadoError()

            # Asigna el identificador del nuevo cliente.
            cliente.idUsuario = self._siguiente_id

            # Prepara la solicitud de bienvenida.
            notificacion = Notificacion(
                idUsuario=cliente.idUsuario,
                correo=cliente.correo
            )

            # Almacena el cliente y su notificación pendiente.
            self._clientes[cliente.idUsuario] = cliente

            try:
                self._notificaciones.append(notificacion)
            except Exception:
                # Revierte el registro si falla el almacenamiento.
                del self._clientes[cliente.idUsuario]
                raise

            self._siguiente_id += 1

            return cliente

    def obtener_notificaciones(self) -> list[Notificacion]:
        # Permite consultar las solicitudes almacenadas.
        with self._lock:
            self._verificar_disponibilidad()

            return self._notificaciones.copy()
