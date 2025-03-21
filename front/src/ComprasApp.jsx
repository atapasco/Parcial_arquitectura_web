import { useState, useEffect } from "react";

export default function ComprasApp() {
  const [producto, setProducto] = useState("");
  const [cantidad, setCantidad] = useState("");
  const [compras, setCompras] = useState([]);
  const [error, setError] = useState(null);

  // Función para obtener las compras
  const obtenerCompras = async () => {
    try {
      const response = await fetch("http://localhost:8000/consulta");
      const data = await response.json();
      console.log("Datos recibidos:", data); // Verifica qué llega
  
      if (data.compras && Array.isArray(data.compras.ordenes)) {
        setCompras(data.compras.ordenes);
      } else {
        console.error("Error: Estructura de datos inesperada", data);
      }
    } catch (error) {
      console.error("Error al obtener compras", error);
    }
  };

  // Llamamos a la función cada 3 segundos para mantener la lista actualizada
  useEffect(() => {
    obtenerCompras();
    const interval = setInterval(obtenerCompras, 3000);
    return () => clearInterval(interval);
  }, []);

  // Función para enviar una nueva orden
  const enviarOrden = async () => {
    if (!producto || !cantidad) {
      console.error("❌ Error: Falta producto o cantidad");
      return;
    }
  
    const orden = { id: Date.now(), producto, cantidad: parseInt(cantidad, 10) };
    console.log("📤 Enviando orden:", orden); // Verifica que los datos están bien
  
    try {
      const response = await fetch("http://localhost:8000/ordenes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(orden),
      });
  
      const data = await response.json();
      console.log("✅ Respuesta de la API:", data);
  
      obtenerCompras(); // Actualizar la lista
    } catch (error) {
      console.error("❌ Error al enviar la orden:", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-6">Sistema de Compras</h1>

      {/* Contenedor principal */}
      <div className="flex flex-col md:flex-row gap-8 items-start w-full max-w-4xl">
        
        {/* Formulario */}
        <div className="bg-white p-6 rounded-lg shadow-md w-full md:w-1/2">
          <input
            type="text"
            placeholder="Producto"
            value={producto}
            onChange={(e) => setProducto(e.target.value)}
            className="w-full p-2 border rounded mb-2"
          />
          <input
            type="number"
            placeholder="Cantidad"
            value={cantidad}
            onChange={(e) => setCantidad(e.target.value)}
            className="w-full p-2 border rounded mb-2"
          />
          <button
            onClick={enviarOrden}
            className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
          >
            Comprar
          </button>
        </div>

        {/* Lista de compras */}
        <div className="w-full md:w-1/2">
          <h2 className="text-xl font-semibold mb-3">Compras registradas</h2>
          <div className="bg-white p-6 rounded-lg shadow-md max-h-80 overflow-y-auto">
            {error && <p className="text-red-500">{error}</p>}
            {compras.length === 0 ? (
              <p className="text-gray-500">No hay compras registradas.</p>
            ) : (
              <ul>
                {compras.map((compra) => (
                  <li key={compra.id} className="border-b p-2">
                    {compra.producto} - {compra.cantidad}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}