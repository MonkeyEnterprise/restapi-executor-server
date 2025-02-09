### Server zijdig:

**Eerste keer starten zonder SSL**
Start de services en laat NGINX draaien zodat Let's Encrypt toegang heeft:

```sh
docker-compose up -d --build
```

**SSL-certificaat ophalen**
Run de Certbot-container:
```sh
docker-compose run certbot
```

**NGINX herstarten met SSL**
```sh
docker-compose restart nginx
```
