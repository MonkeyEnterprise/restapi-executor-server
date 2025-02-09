FROM python:3.8-slim

WORKDIR /app

COPY register_ip.py .

RUN pip install requests

CMD ["python", "register_ip.py"]
