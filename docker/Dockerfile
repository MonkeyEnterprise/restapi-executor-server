# Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

ENV FLASK_APP=main.py
ENV FLASK_ENV=production

CMD ["gunicorn", "main:app", "--workers", "4", "--bind", "0.0.0.0:5000"]