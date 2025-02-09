FROM python:3.11
WORKDIR /app
COPY client.py /app/
RUN pip install socketio-client requests
CMD ["python", "client.py"]
