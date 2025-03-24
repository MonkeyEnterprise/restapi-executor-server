# REST API Executor Server

![REST API Executor Server](assets/api-rest-log.png "REST API Executor Server")

## 1. API Key Authentication

All API requests must include an API key in the request headers.

- **Header Name:** `X-API-Key`
- **Example:**
  ```bash
  curl -X GET http://localhost/ -H "X-API-Key: your_secret_api_key"
  ```

Missing or incorrect API key results in a `401 Unauthorized` error.

---

## 2. Docker Container Management

### Build and Start

```bash
docker-compose up --build -d
```

### Check Running Containers

```bash
docker ps
```

### Stop Containers

```bash
docker-compose down
```

### Restart Containers

```bash
docker-compose up -d
```

### View Logs

```bash
docker logs -f restapi_executor_server
```

---

## 3. API Endpoints

### Server Status

- **Endpoint:** `GET /`
- **Description:** Checks the API server status.

**Example Request:**

```bash
curl -X GET http://localhost/
```

---

### Enqueue a Request

- **Endpoint:** `POST /queue`
- **Content-Type:** `application/json`
- **Description:** Submits a request to the queue.

**Example Request:**

```bash
curl -X POST http://localhost/queue \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_secret_api_key" \
     -d '{"key_1":"value for key 1", "key_2":"value for key 2"}'
```

**Response Codes:**

- `200 OK` – Request successfully queued.
- `400 Bad Request` – Invalid request format.
- `401 Unauthorized` – Missing or incorrect API key.
- `500 Internal Server Error` – Unexpected server error.

**Example Response:**

```json
{
  "status": "queued",
  "uuid": "0f625d48-b366-4679-9c0b-bc2f9b2827cf"
}
```

---

### Get Enqueued Requests

- **Endpoint:** `GET /queue`
- **Description:** Retrieves all enqueued requests.

**Example Request:**

```bash
curl -X GET http://localhost/queue -H "X-API-Key: your_secret_api_key"
```

**Response Codes:**

- `200 OK` – Successfully retrieved enqueued requests.
- `401 Unauthorized` – Missing or incorrect API key.
- `500 Internal Server Error` – Unexpected server error.

**Example Response:**

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

### Delete Enqueued Requests

- **Endpoint:** `POST /queue/delete`
- **Description:** Clears all enqueued requests or deletes a specific request using its unique `UUID`.
- **URL Parameters:**
  - `uuid`: (Optional) UUID of the request to delete. Use `uuid=all` to clear the entire queue.

**Example Request (Clear all):**

```bash
curl -X POST "http://localhost/queue/delete?uuid=all" -H "X-API-Key: your_secret_api_key"
```

**Example Request (Delete specific):**

```bash
curl -X POST "http://localhost/queue/delete?uuid=123e4567-e89b-12d3-a456-426614174000" -H "X-API-Key: your_secret_api_key"
```

**Response Codes:**

- `200 OK` – Requests successfully cleared or specific request removed.
- `400 Bad Request` – UUID parameter missing.
- `401 Unauthorized` – Missing or incorrect API key.
- `404 Not Found` – UUID not found in queue.
- `500 Internal Server Error` – Unexpected server error.

**Example Response (Clear all):**

```json
{
  "status": "cleared"
}
```

**Example Response (Delete specific):**

```json
{
  "status": "removed",
  "uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

## 4. SSL Configuration for Nginx Reverse Proxy

Add the following configuration to use the Nginx reverse proxy with the proper headers:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-API-Key $http_x_api_key;
```
