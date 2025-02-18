# REST API Executor sercer

## **1. Endpoints**
### **Enqueue a Command**
- **Endpoint:** `POST /api/v1/command`
- **Content-Type:** `application/json`
- **Description:** Submits a command to the queue.

##### **Example Request:**
```bash
curl -X POST http://localhost/api/v1/command ^
      -H "Content-Type: application/json" ^
      -d "{\"key_1\":\"value for key 1\", \"key_2\":\"value for key 2\"}" 
```

##### **Response Codes:**
- **`200 OK`** – Command successfully queued.
- **`400 Bad Request`** – Invalid request format.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**
```json
{
  "status": "queued",
  "uuid": "0f625d48-b366-4679-9c0b-bc2f9b2827cf"
}
```
----
### **Get Enqueued Commands**
- **Endpoint:** `GET /api/v1/commands`
- **Description:** Get all enqueued commands.

##### **Example Request:**
```bash
curl -X GET http://localhost/api/v1/commands
```

##### **Response Codes:**
- **`200 OK`** – Successfully retrieved enqueued commands.
- **`404 Not Found`** – No commands in queue.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**
```json
[
  {
    "key_1":"value for key 1",
    "key_2":"value for key 2",
    "uuid":"72d8975d-34ab-4b3b-beaf-57cabcc458e6"
  }
]

```
----
### **Clear All Enqueued Commands**
- **Endpoint:** `DELETE /api/v1/commands`
- **Description:** Clears all enqueued commands.

##### **Example Request:**
```bash
curl -X DELETE http://localhost/api/v1/commands
```

##### **Response Codes:**
- **`200 OK`** – Commands successfully cleared.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**
```json
{
  "message": "Successfully cleared the queued commands"
}
```
----
### **Get Server Status**
- **Endpoint:** `GET /api/v1`
- **Description:** Retrieves the status of the server.

##### **Example Request:**
```bash
curl -X GET http://localhost/api/v1
```

##### **Response Codes:**
- **`200 OK`** – Server is running and reachable.
- **`500 Internal Server Error`** – Unexpected server error.

##### **Example Response:**
```json
{
  "client_ip": "127.0.0.1",
  "message": "You are successfully connected to the REST API server."
}
```
