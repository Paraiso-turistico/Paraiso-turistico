from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError

from app.api.proveedor import router

app = FastAPI(title="Paraiso Turistico")
app.include_router(router)


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a Paraiso Turistico"}


@app.exception_handler(RequestValidationError)
async def validacion(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={
        "mensaje": "Solicitud inválida: revise los campos obligatorios",
        "data": None, "success": False})


@app.exception_handler(OperationalError)
async def no_disponible(request: Request, exc: OperationalError):
    return JSONResponse(status_code=503, content={
        "mensaje": "Servicio temporalmente no disponible. Intente nuevamente más tarde.",
        "data": None, "success": False})


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={
        "mensaje": exc.detail, "data": None, "success": False})


@app.exception_handler(Exception)
async def generico(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={
        "mensaje": "Ocurrió un error inesperado. Intente nuevamente más tarde.",
        "data": None, "success": False})
