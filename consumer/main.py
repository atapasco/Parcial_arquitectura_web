import asyncio
import aio_pika
import asyncpg
import json

# Conexión a la base de datos
async def conectar_db():
    return await asyncpg.connect(
        user="user",
        password="password",
        database="ordenes_db",
        host="db",
        port=5432
    )

# Función para guardar la orden en la base de datos
async def guardar_orden(orden):
    try:
        conn = await conectar_db()
        await conn.execute(
            "INSERT INTO ordenes (id, producto, cantidad) VALUES ($1, $2, $3)",
            orden['id'], orden['producto'], orden['cantidad']
        )
        await conn.close()
        print(f"📥 Orden guardada en la BD: {orden}")
    except Exception as e:
        print(f"❌ Error al guardar en la BD: {e}")

# Consumir mensajes de la cola "ordenes"
async def consumir_ordenes():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("ordenes", durable=True)

        async for message in queue:
            async with message.process():
                orden = json.loads(message.body)
                print(f"📩 Mensaje recibido: {orden}")
                await guardar_orden(orden)

# Función para consultar las órdenes almacenadas
async def obtener_ordenes():
    conn = await conectar_db()
    rows = await conn.fetch("SELECT id, producto, cantidad FROM ordenes")
    await conn.close()
    return [{"id": row["id"], "producto": row["producto"], "cantidad": row["cantidad"]} for row in rows]

# Publicar las órdenes en RabbitMQ
async def publicar_respuesta(ordenes):
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(ordenes).encode()),
            routing_key="ordenes_respuesta"
        )
        print("📤 Respuesta enviada con órdenes:", ordenes)

# Consumir mensajes de la cola "consulta_ordenes"
async def consumir_eventos():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("consulta_ordenes", durable=True)

        async for message in queue:
            async with message.process():
                mensaje = message.body.decode()
                if mensaje == "Solicitar órdenes":
                    ordenes = await obtener_ordenes()
                    await publicar_respuesta(ordenes)

# Ejecución principal
async def main():
    await asyncio.gather(
        consumir_ordenes(),
        consumir_eventos(),
    )

if __name__ == "__main__":
    asyncio.run(main())