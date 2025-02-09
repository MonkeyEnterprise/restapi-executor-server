Eerste keer starten zonder SSL
Start de services en laat NGINX draaien zodat Let's Encrypt toegang heeft:

bash
Code kopiëren
docker compose up -d --build
SSL-certificaat ophalen
Run de Certbot-container:

bash
Code kopiëren
docker compose run certbot
NGINX herstarten met SSL

bash
Code kopiëren
docker compose restart nginx
