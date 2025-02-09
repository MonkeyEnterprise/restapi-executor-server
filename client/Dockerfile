FROM python:3.9-slim

# Installeer de benodigde Python-pakketten
RUN pip install requests

# Kopieer het Python-script naar de container
COPY client.py /app/client.py

# Stel de werkmap in en voer het script uit
WORKDIR /app
CMD ["python", "client.py"]

