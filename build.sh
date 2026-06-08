#!/bin/bash
# ===========================================================================
# build.sh - Script de automatizacion (basado en la estructura sample-app.sh)
#
# Hace TODO el flujo de contenerizacion de forma automatica:
#   1. Prepara un directorio temporal con el codigo de la app.
#   2. GENERA el Dockerfile con comandos echo.
#   3. CONSTRUYE la imagen Docker.
#   4. EJECUTA el contenedor (consulta puntual a la API y termina con exit 0).
#   5. Registra la evidencia (docker ps -a + logs) en evidencias/docker/output.txt
# ===========================================================================

IMAGEN="ipenrichapp"        # nombre de la imagen Docker
CONTENEDOR="samplerunning"  # nombre del contenedor (coincide con el pipeline)

# --- 0. Limpieza previa para que el script sea reproducible (idempotente) ---
rm -rf tempdir
docker rm -f "$CONTENEDOR" 2>/dev/null   # borra contenedor anterior si existe

# --- 1. Crear estructura temporal y copiar el codigo ---
mkdir tempdir
cp app.py tempdir/.
cp requirements.txt tempdir/.

# --- 2. Generar el Dockerfile dentro de tempdir ---
echo "FROM python:3.11-slim"                         >  tempdir/Dockerfile
echo "WORKDIR /home/myapp"                           >> tempdir/Dockerfile
echo "COPY requirements.txt /home/myapp/"            >> tempdir/Dockerfile
echo "RUN pip install --no-cache-dir -r requirements.txt" >> tempdir/Dockerfile
echo "COPY app.py /home/myapp/"                       >> tempdir/Dockerfile
echo "CMD python3 /home/myapp/app.py"                >> tempdir/Dockerfile

# --- 3. Construir la imagen ---
cd tempdir
docker build -t "$IMAGEN" .

# --- 4. Ejecutar el contenedor ---
#   -e  inyecta las variables de entorno SIN escribirlas en la imagen (seguro).
#   Sin -d: corre en primer plano, imprime los datos de la API y termina (exit 0).
docker run --name "$CONTENEDOR" \
  -e IPINFO_TOKEN="$IPINFO_TOKEN" \
  -e TARGET_IP="$TARGET_IP" \
  "$IMAGEN"

# --- 5. Registrar evidencia (se sobrescribe en cada ejecucion) ---
mkdir -p ../evidencias/docker
SALIDA="../evidencias/docker/output.txt"
{
  echo "===================== docker ps -a ====================="
  docker ps -a
  echo ""
  echo "================== docker logs $CONTENEDOR =============="
  docker logs "$CONTENEDOR"
} > "$SALIDA"

# Mostrar tambien por consola el estado final
echo ""
echo "===================== docker ps -a ====================="
docker ps -a
