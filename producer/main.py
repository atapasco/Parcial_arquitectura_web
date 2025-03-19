import pika
import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Orden(BaseModel):
    id: int
    producto: str
    cantidad: int

def publicar_evento(orden: Orden):
    """Publica la orden en RabbitMQ"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ordenes')
    
    mensaje = orden.model_dump_json()
    channel.basic_publish(exchange='', routing_key='ordenes', body=mensaje)
    
    connection.close()
    
def publicar_evento_consulta():
    """Publica un mensaje en RabbitMQ para solicitar las órdenes."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    
    channel.queue_declare(queue="consulta_ordenes")
    channel.basic_publish(exchange="", routing_key="consulta_ordenes", body="Solicitar órdenes")
    
    print("📤 Evento de consulta de órdenes enviado")
    connection.close()

def esperar_respuesta(timeout=5):
    """Espera la respuesta del consumidor con las órdenes almacenadas."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="ordenes_respuesta")

    resultado = None

    def callback(ch, method, properties, body):
        nonlocal resultado
        resultado = json.loads(body)
        ch.stop_consuming()

    channel.basic_consume(queue="ordenes_respuesta", on_message_callback=callback, auto_ack=True)

    print("⏳ Esperando respuesta del consumidor...")
    start_time = time.time()

    while resultado is None:
        connection.process_data_events(time_limit=1)  # Procesa eventos
        if time.time() - start_time > timeout:  # Si excede el tiempo de espera, lanza error
            print("⏳ Tiempo de espera agotado. No se recibió respuesta del consumidor.")
            connection.close()
            raise HTTPException(status_code=504, detail="Tiempo de espera agotado. No se recibió respuesta del consumidor")

    connection.close()
    return resultado


@app.post("/publicar")
def publicar(orden: Orden):
    try:
        publicar_evento(orden)
        return {"mensaje": "Orden enviada a RabbitMQ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/consultar")
def consultar():
    try:
        publicar_evento_consulta()
        respuesta = esperar_respuesta()
        return {"ordenes": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))