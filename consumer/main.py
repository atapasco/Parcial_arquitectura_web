import pika
import psycopg2
import json
import threading

# Conexión a la base de datos
def conectar_db():
    return psycopg2.connect(
        dbname="ordenes_db",
        user="user",
        password="password",
        host="db",
        port="5432"
    )

# Función para guardar la orden en la base de datos
def guardar_orden(orden):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ordenes (id, producto, cantidad) VALUES (%s, %s, %s)",
        (orden['id'], orden['producto'], orden['cantidad'])
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"📥 Orden guardada en la BD: {orden}")

# Función para procesar eventos desde RabbitMQ
def procesar_orden(ch, method, properties, body):
    try:
        orden = json.loads(body)
        guardar_orden(orden)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmar procesamiento
    except Exception as e:
        print("❌ Error al procesar la orden:", e)

# Consumir mensajes de RabbitMQ
def consumir_ordenes():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='ordenes')

    channel.basic_consume(queue='ordenes', on_message_callback=procesar_orden, auto_ack=False)
    print("🚀 Esperando órdenes y guardándolas en la BD...")
    channel.start_consuming()

# Función para consultar las órdenes almacenadas
def obtener_ordenes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, producto, cantidad FROM ordenes")
    ordenes = [{"id": row[0], "producto": row[1], "cantidad": row[2]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ordenes

# Publicar las órdenes en RabbitMQ
def publicar_respuesta(ordenes):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="ordenes_respuesta")

    mensaje = json.dumps(ordenes)
    channel.basic_publish(exchange="", routing_key="ordenes_respuesta", body=mensaje)
    print("📤 Respuesta enviada con órdenes:", ordenes)

# Procesar eventos desde RabbitMQ
def procesar_evento(ch, method, properties, body):
    mensaje = body.decode()
    
    if mensaje == "Solicitar órdenes":
        ordenes = obtener_ordenes()
        publicar_respuesta(ordenes)

# Consumir mensajes de RabbitMQ
def consumir_eventos():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()
    
    channel.queue_declare(queue="ordenes")
    channel.basic_consume(queue="ordenes", on_message_callback=procesar_evento, auto_ack=True)

    channel.queue_declare(queue="consulta_ordenes")
    channel.basic_consume(queue="consulta_ordenes", on_message_callback=procesar_evento, auto_ack=True)

    print("🚀 Esperando eventos...")
    channel.start_consuming()

if __name__ == "__main__":
    hilo_ordenes = threading.Thread(target=consumir_ordenes)
    hilo_eventos = threading.Thread(target=consumir_eventos)

    hilo_ordenes.start()
    hilo_eventos.start()

    hilo_ordenes.join()
    hilo_eventos.join()