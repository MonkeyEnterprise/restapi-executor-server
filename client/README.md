###Bouw de Docker-container:

Open een terminal in de map waar je Dockerfile en client.py hebt opgeslagen, en voer het volgende uit:

```bash
docker build -t propresenter-client .
```

Na het bouwen van de container kun je de client starten met het volgende commando:

```bash
docker run -d --name propresenter-client propresenter-client
```
