from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from enum import Enum

# ---------- Base de datos ----------
motor = create_engine("sqlite:///./paraiso.db")
Sesion = sessionmaker(bind=motor)
Base = declarative_base()


class ProveedorORM(Base):
    __tablename__ = "proveedor"
    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    nombre_comercial = Column(String(200), nullable=False)
    documento_tributario = Column(String(50), nullable=False, unique=True)
    correo = Column(String(150))
    telefono = Column(String(50))
    tipo_proveedor = Column(String(30), nullable=False)
    estado = Column(String(20), nullable=False, default="ACTIVO")


Base.metadata.create_all(bind=motor)

# ---------- Tipos permitidos ----------
class TipoProveedor(str, Enum):
    HOSPEDAJE = "HOSPEDAJE"
    RESTAURANTE = "RESTAURANTE"
    RECREACION = "RECREACION"


# ---------- Formatos ----------
class DatosProveedor(BaseModel):
    nombreComercial: str
    documentoTributario: str
    correo: str | None = None
    telefono: str | None = None
    tipoProveedor: str


class Respuesta(BaseModel):
    mensaje: str
    data: dict | None = None
    success: bool


# ---------- Seguridad (Caso 2 y Caso 6) ----------
esquema = HTTPBearer(auto_error=False)

# En desarrollo usamos tokens fijos. En producción vendrían de un JWT real.
TOKENS = {
    "token-admin": {"usuario": "admin", "rol": "ADMINISTRADOR"},
    "token-cliente": {"usuario": "cliente1", "rol": "CLIENTE"},
}


def solo_administrador(cred: HTTPAuthorizationCredentials | None = Depends(esquema)):
    if cred is None or cred.credentials not in TOKENS:
        raise HTTPException(status_code=401, detail="No autenticado")
    datos = TOKENS[cred.credentials]
    if datos["rol"] != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="No tiene permisos para registrar proveedores")
    return datos


# ---------- Endpoint (Caso 1) ----------
router = APIRouter(prefix="/api/v1/admin", tags=["Proveedores"])


@router.post("/proveedores", status_code=201, response_model=Respuesta)
def registrar_proveedor(datos: DatosProveedor, admin=Depends(solo_administrador)):

    if datos.tipoProveedor not in TipoProveedor.__members__:
        raise HTTPException(status_code=400, detail=(
            "Tipo de proveedor no permitido. Use HOSPEDAJE, RESTAURANTE o RECREACION"))

    sesion = Sesion()

    repetido = sesion.query(ProveedorORM).filter_by(
        documento_tributario=datos.documentoTributario).first()
    if repetido:
        sesion.close()
        raise HTTPException(status_code=409, detail=(
            f"Ya existe un proveedor con el documento {datos.documentoTributario}"))

    fila = ProveedorORM(
        nombre_comercial=datos.nombreComercial,
        documento_tributario=datos.documentoTributario,
        correo=datos.correo,
        telefono=datos.telefono,
        tipo_proveedor=datos.tipoProveedor,
        estado="ACTIVO",
    )
    sesion.add(fila)
    sesion.commit()
    sesion.refresh(fila)
    sesion.close()

    return Respuesta(
        mensaje="Proveedor registrado correctamente",
        data={
            "idProveedor": fila.id_proveedor,
            "nombreComercial": fila.nombre_comercial,
            "tipoProveedor": fila.tipo_proveedor,
            "estado": fila.estado,
        },
        success=True,
    )


# ---------- Endpoint para ver los proveedores creados ----------
@router.get("/proveedores", tags=["Proveedores"])
def listar_proveedores(admin=Depends(solo_administrador)):
    sesion = Sesion()
    filas = sesion.query(ProveedorORM).all()
    sesion.close()
    return {
        "mensaje": "Listado de proveedores",
        "data": [
            {
                "idProveedor": f.id_proveedor,
                "nombreComercial": f.nombre_comercial,
                "documentoTributario": f.documento_tributario,
                "tipoProveedor": f.tipo_proveedor,
                "estado": f.estado,
            }
            for f in filas
        ],
        "success": True,
    }
