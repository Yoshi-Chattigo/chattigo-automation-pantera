FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar bot y archivos necesarios
COPY . .

# Ejecutar bot
CMD ["python", "discord_bot.py"]
