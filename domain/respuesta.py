
from typing import Literal
from pydantic import BaseModel

from domain.cliente import ClienteResponse


# Modelo para respuestas de registro exitoso.
class RespuestaExitosa(BaseModel):
    mensaje: str
    data: ClienteResponse
    success: Literal[True] = True


# Modelo para respuestas de error.
class RespuestaError(BaseModel):
    mensaje: str
    data: None = None
    success: Literal[False] = False
