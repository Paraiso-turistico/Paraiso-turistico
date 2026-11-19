from pydantic import BaseModel, ConfigDict, Field, EmailStr


# Modelo de entrada
class ClienteCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    documento: str = Field(..., min_length=1)
    correo: EmailStr
    telefono: str = Field(..., min_length=1)
    contrasena: str = Field(..., min_length=1)


# Modelo de salida
class ClienteResponse(BaseModel):
    idUsuario: int
    nombres: str
    rol: str
    estado: str


# Entidad interna del dominio
class Cliente:
    def __init__(
        self,
        idUsuario: int,
        nombres: str,
        apellidos: str,
        documento: str,
        correo: str,
        telefono: str,
        contrasena_hash: str
    ):
        self.idUsuario = idUsuario
        self.nombres = nombres
        self.apellidos = apellidos
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        self.contrasena_hash = contrasena_hash
        self.rol = "CLIENTE"
        self.estado = "ACTIVO"

    def to_response(self) -> dict:
        return {
            "idUsuario": self.idUsuario,
            "nombres": self.nombres,
            "rol": self.rol,
            "estado": self.estado
        }