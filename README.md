# Propresenter 7 client executor 

## Server
This script implements a **Flask-based REST API server** with a **thread-safe command queue** for managing and processing commands.

### **Key Features**
- Runs a **Flask REST API server** to handle requests.
- Implements a **CommandQueue** to manage incoming commands and responses.
- Utilizes **multithreading** to process commands asynchronously.
- Includes **logging and argument parsing** for debugging and configuration.

### **Main Components**
#### **1. CommandQueue (Class)**
- Manages incoming commands and their responses in a **thread-safe** manner.
- Uses a locking mechanism to ensure concurrency safety.

#### **2. API Routes**
- Handles requests to enqueue commands, retrieve pending commands, and fetch responses.
- Endpoints:
  - `api/v1` → Get the status of the server.
  - `api/v1/enqueue` → Add a command to the queue.
  - `api/v1/get_commands` → Retrieve all queued commands.
  - `api/v1/fetch_response` → Get the response for a processed command.

#### **3. Server Initialization**
- The Flask server is initialized and configured based on command-line arguments.
- Can be run as a standalone service.

This script is designed to facilitate **communication between a client and a remote executor**, ensuring commands are processed in an orderly manner.
