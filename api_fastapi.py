from fastapi import FastAPI
from typing import Optional

# 1. Crear la instancia de la aplicación
app = FastAPI(
    title="Mi API de Repoblamiento",
    description="API básica para pruebas",
    version="1.0.0"
)

# 2. Endpoint de prueba (GET)
@app.get("/")
def read_root():
    return {"mensaje": "¡API funcionando correctamente!"}

# 3. Endpoint con parámetros de ruta y consulta
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {
        "item_id": item_id,
        "busqueda": q,
        "estado": "procesado"
    }

# 4. Endpoint POST para recibir datos (Simulacro de login o SP)
@app.post("/ejecutar")
def ejecutar_accion(datos: dict):
    # Aquí podrías integrar tu clase ConexionSQL

    return {"resultado": "Acción recibida", "datos_recibidos": datos}
