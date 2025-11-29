FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY bot/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del bot
COPY bot/ .

# Mostrar contenido del contenedor para DEBUG
RUN ls -la /app

# Comando de ejecución
CMD ["python", "discord_bot.py"]
