# Dockerfile para el frontend en Node.js
FROM node:22

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios
COPY package.json package-lock.json ./

# Instala las dependencias
RUN npm install

# Copia el resto de los archivos
COPY . .

# Exponer el puerto que usa tu frontend (por ejemplo, 5173 para Vite o 3000 para Next.js)
EXPOSE 5173

# Comando para ejecutar la aplicación
CMD ["npm", "run", "dev"]