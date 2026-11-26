from datetime import datetime, timezone


# Entidad que representa una solicitud de bienvenida.
class Notificacion:

    def __init__(self, idUsuario: int, correo: str):
        self.idUsuario = idUsuario
        self.correo = correo

        # Define el tipo y estado inicial de la notificación.
        self.tipo = "BIENVENIDA"
        self.estado = "PENDIENTE"

        # Registra la fecha y hora de creación.
        self.fecha_creacion = datetime.now(timezone.utc)