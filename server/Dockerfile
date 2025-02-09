FROM python:3.11
WORKDIR /app
COPY app.py /app/
RUN pip install flask flask-socketio requests eventlet
CMD ["python", "app.py"]
