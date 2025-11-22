# Imagen base
FROM python:3.11-slim

# Evita crear archivos .pyc y usa un buffer más rápido
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Crea el directorio del proyecto
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer puerto (Gunicorn usa 8000 por defecto)
EXPOSE 8000

# Comando de producción con Gunicorn
CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]
