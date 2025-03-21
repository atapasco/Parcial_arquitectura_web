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
    <div className="app-container">
      <div className="form-and-list-container">
        <h1 className="main-title">Sistema de Compras</h1>
  
        {/* Contenedor del formulario y la tabla */}
        <div className="inner-container">
          {/* Formulario */}
          <div className="form-container">
            <label htmlFor="producto" className="form-label">
              Producto
            </label>
            <input
              id="producto"
              type="text"
              placeholder="Nombre del producto"
              value={producto}
              onChange={(e) => setProducto(e.target.value)}
              className="input-field"
            />
  
            <label htmlFor="cantidad" className="form-label">
              Cantidad
            </label>
            <input
              id="cantidad"
              type="number"
              placeholder="Cantidad"
              value={cantidad}
              onChange={(e) => setCantidad(e.target.value)}
              className="input-field"
            />
  
            <button onClick={enviarOrden} className="submit-button">
              Comprar
            </button>
          </div>
  
          {/* Lista de compras */}
          <div className="list-container">
            <h2 className="list-title">Compras registradas</h2>
            <div className="scrollable-list">
              {error && <p className="error-message">{error}</p>}
              {compras.length === 0 ? (
                <p className="empty-message">No hay compras registradas.</p>
              ) : (
                <table className="purchase-table">
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Cantidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {compras.map((compra) => (
                      <tr key={compra.id}>
                        <td>{compra.producto}</td>
                        <td>{compra.cantidad}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}