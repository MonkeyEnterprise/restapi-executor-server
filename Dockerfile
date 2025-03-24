FROM python:3.12-slim
WORKDIR /app
COPY app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ /app
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "main:app"]
