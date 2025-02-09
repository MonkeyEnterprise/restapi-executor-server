# Gebruik een officiële Python runtime als basis
FROM python:3.9-slim

# Stel de werkdirectory in
WORKDIR /app

# Kopieer het requirements-bestand en installeer de afhankelijkheden
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de servercode naar de container
COPY . /app

# Stel het commando in om de Flask server te starten
CMD ["python", "server.py"]
