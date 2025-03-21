from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir React
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
)

RABBITMQ_PRODUCER_URL = "http://producer:8001/publicar"
RABBITMQ_PRODUCER_URL2 = "http://producer:8001/consultar"

@app.post("/ordenes")
def crear_orden(orden: dict):
    """Recibe una orden y la envía al productor"""
    response = requests.post(RABBITMQ_PRODUCER_URL, json=orden)
    return {"mensaje": "Orden enviada", "respuesta": response.json()}

@app.get("/consulta")
def consulta():
    response = requests.get(RABBITMQ_PRODUCER_URL2)
    return {"compras": response.json()}