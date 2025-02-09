
### **Nginx API Parentpager Gateway Setup for Docker used for Propresenter 7**

This setup creates an **NGINX API Gateway** running in a **Docker container**. The gateway listens on port **6410** and forwards specific endpoints to a backend service running on **localhost:5000**. The gateway only accepts **GET** and **POST** requests for the `/v1/stage/state` and `/version` endpoints.

---

### **1. Build the Docker Container**

Open a terminal in the directory where `Dockerfile` and `nginx.conf` are located and run the following command:

```sh
docker build -t nginx_api_gateway .
```

---

### **2. Start the Container**

Run the container and map port 6410 to the host:

```sh
docker run --name api-gateway -p 6410:6410 -d nginx_api_gateway
```

---

### **3. Check if the Container is Running**

To see if the container is running, use the following command:

```sh
docker ps
```

---

### **4. View the Container Logs**

If there are any issues, view the logs using:

```sh
docker logs api-gateway
```

---

### **5. Auto-Restart on System Reboot**

If you want the container to automatically restart upon Windows reboot, you can run the container with the `--restart` option:

```sh
docker run --name api-gateway -p 6410:6410 -d --restart always nginx_api_gateway
```

---

This setup will create a lightweight **API Gateway** with NGINX, forwarding specific endpoints to the backend server, making it a simple solution for managing API traffic in Dockerized environments.
