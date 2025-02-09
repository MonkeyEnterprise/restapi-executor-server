FROM python:3.8-slim

WORKDIR /app

COPY flask_app.py .

RUN pip install flask requests

CMD ["python", "flask_app.py"]
