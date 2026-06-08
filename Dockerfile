cat > ~/docker-toolkit/Dockerfile << 'ENDOFFILE'
# Imagen base oficial Python en Alpine (minimalista)
FROM python:3.11-alpine

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar primero requirements.txt para aprovechar la caché de Docker
# Si el código cambia pero las dependencias no, esta capa se reutiliza
COPY app/requirements.txt .

# Instalar dependencias sin caché de pip para reducir tamaño de imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY app/ .

# Documentar el puerto que usa la aplicación
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
ENDOFFILE