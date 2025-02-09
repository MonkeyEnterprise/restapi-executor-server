### **Nginx API Parentpager Gateway Setup for Docker used for Propresenter 7**

This setup creates an **NGINX API Gateway** running in a **Docker container**. The gateway listens on port **6410** and forwards specific endpoints to a backend service running on **localhost:5000**. The gateway only accepts **GET** and **POST** requests for the `/v1/stage/state` and `/version` endpoints.

---

### **1. Build the Docker Container**

Start de containers en vraag het SSL-certificaat aan

Voer deze commando's uit:
```sh
cd ~/nginx-api-gateway
docker-compose up -d
```

Als het certificaat correct wordt gegenereerd, herstart je NGINX met:

```sh
docker restart api-gateway
```

---

### **2. Test server**
Check HTTP redirect:

```sh
curl -I http://parentpager.pouwertronics.nl
```
Dit zou een 301 Redirect naar HTTPS moeten geven.

**Test API-key beveiliging:**

```sh
curl -H "X-API-KEY: JOUW-GEHEIME-API-KEY" https://parentpager.pouwertronics.nl/version
```
Dit zou een 200 OK moeten geven als de key correct is.

---
