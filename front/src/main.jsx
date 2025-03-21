import React from "react";
import ReactDOM from "react-dom/client";
import ComprasApp from "./ComprasApp"; // Asegúrate de que el nombre coincide con tu archivo
import "./index.css"; // Asegúrate de que este archivo existe

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ComprasApp />
  </React.StrictMode>
);