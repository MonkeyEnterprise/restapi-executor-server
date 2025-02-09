# Basisimage (gebruik Python 3.9 of nieuwer)
FROM python:3.9-slim

# Werkdirectory instellen
WORKDIR /app

# Vereiste pakketten installeren
RUN pip install --upgrade pip

# Kopieer eerst alleen requirements.txt om caching te benutten
COPY requirements.txt .

# Installeer de afhankelijkheden
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer de rest van de applicatiebestanden
COPY . .

# Poort openen
EXPOSE 5000

# Container opstarten
CMD ["python", "app.py"]
