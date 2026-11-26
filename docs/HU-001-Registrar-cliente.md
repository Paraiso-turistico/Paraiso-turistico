
# HU-001 - Registrar cliente

## 1. Descripción

Como visitante sin una cuenta registrada, quiero crear
una cuenta de cliente en Paraíso Turístico para consultar
y reservar servicios turísticos.

## 2. Objetivo

Implementar un servicio REST que permita registrar clientes,
validar sus datos, garantizar la unicidad del correo y
documento, proteger la contraseña y generar una solicitud
de notificación de bienvenida.

## 3. Arquitectura

La implementación utiliza una arquitectura por capas:

| Capa | Responsabilidad |
|---|---|
| API | Recibir peticiones HTTP y generar respuestas. |
| Domain | Definir entidades y modelos de datos. |
| Service | Ejecutar la lógica de negocio. |
| Repository | Administrar el almacenamiento en memoria. |
| Tests | Verificar el funcionamiento del sistema. |

### Flujo de ejecución

1. Recibir los datos del cliente.
2. Validar los campos obligatorios, formatos y tipos.
3. Verificar que el correo no esté registrado.
4. Verificar que el documento no esté registrado.
5. Generar el hash de la contraseña.
6. Asignar el rol CLIENTE y el estado ACTIVO.
7. Almacenar el cliente en memoria.
8. Registrar la solicitud de bienvenida.
9. Retornar una respuesta HTTP 201.

## 4. Contrato del servicio REST

- Método: POST
- Endpoint: /api/v1/auth/clientes
- Formato: application/json
- Autenticación: no requerida.

### 4.1. Datos de entrada

| Campo | Tipo | Obligatorio |
|---|---|---|
| nombres | String | Sí |
| apellidos | String | Sí |
| documento | String | Sí |
| correo | String (Email) | Sí |
| telefono | String | Sí |
| contrasena | String | Sí |

Ejemplo de petición:

```json
{
    "nombres": "Laura",
    "apellidos": "Martinez",
    "documento": "1098765432",
    "correo": "laura@example.com",
    "telefono": "3109876543",
    "contrasena": "ClavePrueba2026!"
}
```

### 4.2. Respuesta exitosa

HTTP 201 Created.

```json
{
    "mensaje": "Cliente registrado correctamente",
    "data": {
        "idUsuario": 101,
        "nombres": "Laura",
        "rol": "CLIENTE",
        "estado": "ACTIVO"
    },
    "success": true
}
```

### 4.3. Códigos de respuesta

| Código | Descripción |
|---|---|
| 201 | Cliente registrado correctamente. |
| 400 | Datos inválidos o incompletos. |
| 409 | Correo o documento duplicado. |
| 503 | Servicio temporalmente no disponible. |
| 500 | Error interno del servidor. |

Las respuestas de error mantienen la siguiente estructura:

```json
{
    "mensaje": "Descripción del error",
    "data": null,
    "success": false
}
```

## 5. Seguridad

- Validación de datos mediante Pydantic.
- Validación estricta de tipos.
- Rechazo de campos adicionales no autorizados.
- Asignación automática del rol CLIENTE.
- Protección de contraseñas mediante el algoritmo scrypt.
- Generación de un salt aleatorio para cada contraseña.
- Exclusión de la contraseña y su hash de las respuestas.
- Mensajes genéricos para errores internos.

## 6. Almacenamiento

Por requerimiento académico, los clientes y las solicitudes
de bienvenida se almacenan en memoria.

El repositorio utiliza un mecanismo de bloqueo (Lock) para
controlar el acceso concurrente al almacenamiento.

Si ocurre un fallo durante el almacenamiento de la
notificación, se revierte el registro del cliente para
evitar inconsistencias.

No se utiliza una base de datos externa ni se implementan
transacciones de base de datos.

## 7. Notificación de bienvenida

Después del registro se genera una solicitud de
notificación con los siguientes datos:

- Identificador del cliente.
- Correo electrónico.
- Tipo: BIENVENIDA.
- Estado: PENDIENTE.
- Fecha de creación.

La implementación registra la solicitud, pero no realiza
el envío efectivo de correos electrónicos.

## 8. Pruebas automatizadas

Las pruebas fueron desarrolladas utilizando pytest.

| Grupo | Pruebas | Superadas | Fallidas |
|---|---:|---:|---:|
| Repositorio | 8 | 8 | 0 |
| Servicio | 8 | 8 | 0 |
| API | 12 | 12 | 0 |
| Total | 28 | 28 | 0 |

Resultado de la ejecución conjunta del 26/11/2026:

```text
28 passed, 1 warning in 1.28s
```

Las pruebas verifican el registro exitoso, duplicados,
validación de datos, seguridad, notificaciones,
disponibilidad, reversión ante fallos y contrato HTTP.

Los errores 500 y 503 fueron comprobados mediante
simulación de fallos en las pruebas automatizadas.

## 9. Pruebas funcionales en Postman

| Escenario | HTTP esperado | Resultado |
|---|---|---|
| Registro exitoso | 201 | Superado |
| Correo duplicado | 409 | Superado |
| Documento duplicado | 409 | Superado |
| Correo inválido | 400 | Superado |
| Campo obligatorio faltante | 400 | Superado |
| Tipo de dato incorrecto | 400 | Superado |
| Rol no autorizado | 400 | Superado |

Total: 7 de 7 escenarios superados.

Colección de Postman:

[HU-001 - Registrar cliente](postman/HU-001-Registrar-cliente.postman_collection.json)

Para reproducir las pruebas:

1. Iniciar la API con el repositorio vacío.
2. Importar la colección en Postman.
3. Ejecutar las peticiones numeradas del 01 al 07.
4. Verificar los códigos HTTP y cuerpos de respuesta.

## 10. Documentación OpenAPI

Swagger UI:

http://127.0.0.1:8000/docs

Especificación OpenAPI:

http://127.0.0.1:8000/openapi.json

## 11. Ejecución del proyecto

Desde la raíz del proyecto y con el entorno virtual activo,
instalar las dependencias:

```powershell
python -m pip install -r requirements.txt
```

Iniciar el servidor:

```powershell
python -m uvicorn main:app --reload
```

Ejecutar las pruebas automatizadas:

```powershell
python -m pytest tests/ -v
```

## 12. Consideraciones y limitaciones

- El almacenamiento es temporal y se pierde al reiniciar
  el servidor.
- No se realiza el envío real de correos electrónicos.
- Los fallos 500 y 503 se verificaron mediante simulación.
- Se presentó una advertencia de obsolescencia relacionada
  con httpx y Starlette TestClient, sin afectar los
  resultados de las pruebas.
- La implementación y las pruebas se realizaron localmente.
- La integración con las demás funcionalidades del
  proyecto está pendiente.
