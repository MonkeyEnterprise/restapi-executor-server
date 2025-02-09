# propresenter-parent-pager-gateway

Open een terminal in de map waar `Dockerfile` en `nginx.conf` staan, en voer het volgende commando uit:

```sh
docker build -t nginx_api_gateway .
```

### Start de container

Run de container en map poort 6410 naar de host:

```sh
docker run --name api-gateway -p 6410:6410 -d nginx_api_gateway
```

### Controleer of de container draait

Bekijk of de container actief is:

```sh
docker ps
```

### Bekijk de logs van de container

Als je problemen ondervindt, kun je de logs bekijken met:

```sh
docker logs api-gateway
```

### Automatisch opnieuw starten bij opstarten

Als je wilt dat de container automatisch opnieuw start bij het opstarten van Windows, kun je de container draaien met de `--restart` optie:

```sh
docker run --name api-gateway -p 6410:6410 -d --restart always nginx_api_gateway
```
