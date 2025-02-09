---
### Server zijdig:

**Eerste keer starten zonder SSL**
Start de services en laat NGINX draaien zodat Let's Encrypt toegang heeft:
```bash
docker compose up -d --build
```

**SSL-certificaat ophalen**
Run de Certbot-container:
```bash
docker compose run certbot
```

**NGINX herstarten met SSL**
```bash
docker compose restart nginx
```
---
