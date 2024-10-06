# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /programas/api-orquestador

# Instalar las dependencias de Python directamente (sin archivo requirements.txt)
RUN pip install --no-cache-dir Flask requests

# Copiar el código fuente del microservicio en el contenedor
COPY . .

# Exponer el puerto que utiliza el microservicio
EXPOSE 8004

# Comando para ejecutar la aplicación Flask
CMD ["python", "microservicioOrquestador.py"]
