# REST API Executor Server v1.0.1

![REST API Executor Server](assets/api-rest-log.png "REST API Executor Server")

## **1. API Key Authentication**

All API requests must include an API key for authentication. The key should be passed in the request headers.

- **Header Name:** `X-API-Key`
- **Example Usage:**
  ```bash
  curl -X GET http://localhost/api/v1 \
       -H "X-API-Key: your_secret_api_key"
  ```

If the API key is missing or incorrect, the server will respond with a `401 Unauthorized` error.

---

## **2. How to Start the Docker Container**

### **Build and Start the Containers**

To build and start the API server and Nginx reverse proxy, use the following command:

```bash
docker-compose up --build -d
```

This command:
- Builds the necessary Docker images.
- Starts the containers in detached mode (`-d`).

### **Check Running Containers**

To verify that the containers are running, execute:

```bash
docker ps
```

### **Stop the Containers**

To stop the running containers, use:

```bash
docker-compose down
```

This will shut down and remove the containers.

### **Restart the Containers**

If the containers are already built and you want to restart them:

```bash
docker-compose up -d
```

### **View Logs**

To check the logs of the running API server:

```bash
docker logs -f restapi_executor_server
```

---

## **3. API Endpoints**

### **Enqueue a Command**

- **Endpoint:** `POST /api/v1/command`
- **Content-Type:** `application/json`
- **Description:** Submits a command to the queue.

##### **Example Request:**

```bash
curl -X POST http://localhost/api/v1/command \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_secret_api_key" \
     -d '{"key_1":"value for key 1", "key_2":"value for key 2"}'
```

##### **Response Codes:**

- **`200 OK`** – Command successfully queued.
- **`400 Bad Request`** – Invalid request format.
- **`401 Unauthorized`** – Missing or incorrect API key.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**

```json
{
  "status": "queued",
  "uuid": "0f625d48-b366-4679-9c0b-bc2f9b2827cf"
}
```

---

### **Get Enqueued Commands**

- **Endpoint:** `GET /api/v1/commands`
- **Description:** Retrieve all enqueued commands.

##### **Example Request:**

```bash
curl -X GET http://localhost/api/v1/commands \
     -H "X-API-Key: your_secret_api_key"
```

##### **Response Codes:**

- **`200 OK`** – Successfully retrieved enqueued commands.
- **`401 Unauthorized`** – Missing or incorrect API key.
- **`404 Not Found`** – No commands in queue.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**

```json
[
  {
    "key_1": "value for key 1",
    "key_2": "value for key 2",
    "uuid": "72d8975d-34ab-4b3b-beaf-57cabcc458e6"
  }
]
```

---

### **Clear All Enqueued Commands**

- **Endpoint:** `DELETE /api/v1/commands`
- **Description:** Clears all enqueued commands.

##### **Example Request:**

```bash
curl -X DELETE http://localhost/api/v1/commands \
     -H "X-API-Key: your_secret_api_key"
```

##### **Response Codes:**

- **`200 OK`** – Commands successfully cleared.
- **`401 Unauthorized`** – Missing or incorrect API key.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**

```json
{
  "message": "Successfully cleared the queued commands"
}
```

---

### **Clear a Specific Enqueued Command**

- **Endpoint:** `DELETE /api/v1/command`
- **Description:** Removes a specific command from the queue using its unique `UUID`.
  The request must include a valid **API key** for authentication.

##### **Example Request:**

```bash
curl -X DELETE http://localhost/api/v1/command ^
     -H "Content-Type: application/json" ^
     -H "X-API-Key: your_secret_api_key" ^
     -d '{"uuid": "123e4567-e89b-12d3-a456-426614174000"}'
```

##### **Response Codes:**

- **`200 OK`** – Command successfully removed.
- **`401 Unauthorized`** – Missing or incorrect API key.
- **`404 Not Found`** – UUID not found in queue.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**

```json
{
  "message": "Successfully removed command with UUID 123e4567-e89b-12d3-a456-426614174000"
}
```

---

## **4. SSL Configuration for Nginx Reverse Proxy**

To use the Nginx reverse proxy with the proper headers, add the following configuration:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-API-Key $http_x_api_key;
```

