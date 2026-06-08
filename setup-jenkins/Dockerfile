# Imagen de Jenkins que incluye el cliente de Docker.
# Necesaria para que Jenkins pueda ejecutar 'docker build' y 'docker run'
# usando el Docker de tu computador (Docker Desktop) a traves del socket.
FROM jenkins/jenkins:lts
USER root
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*
USER jenkins
