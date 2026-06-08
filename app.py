#!/usr/bin/env python3
"""
IP Enrichment Tool - Herramienta de enriquecimiento de direcciones IP.

Stakeholder: Analista de seguridad de red (SOC/NOC).
Problema   : Cuando una alerta de red (p. ej. un NDR como Darktrace) marca una
             conexion hacia una IP publica desconocida, el analista necesita
             saber rapidamente QUIEN es el dueno de esa IP (pais, ciudad,
             ISP/ASN, zona horaria) para decidir si la conexion es legitima
             (un CDN, un cloud) o sospechosa. Hacerlo a mano por cada IP es
             lento durante el triage de un incidente.
Solucion   : Esta herramienta hace UNA consulta puntual a la API externa
             ipinfo.io, procesa los datos y entrega un informe por consola.

La clave de la API NUNCA se escribe en el codigo: se lee del sistema con la
libreria 'os' (variable de entorno IPINFO_TOKEN).
"""

import os
import sys
import requests


# ---------------------------------------------------------------------------
# 1. CONFIGURACION (todo viene de variables de entorno, nada hardcodeado)
# ---------------------------------------------------------------------------
API_HOST = "https://ipinfo.io"          # URL base de la API externa
TIMEOUT = 10                            # segundos antes de cortar la peticion


def obtener_token():
    """Lee el token desde la variable de entorno. Si no existe, aborta."""
    token = os.getenv("IPINFO_TOKEN")
    if not token:
        print("[ERROR] No se encontro la variable de entorno IPINFO_TOKEN.")
        print("        Configurela antes de ejecutar:")
        print('          Linux/Bash : export IPINFO_TOKEN="tu_token"')
        print('          Windows PS : $env:IPINFO_TOKEN = "tu_token"')
        sys.exit(1)
    return token


def obtener_ip_objetivo():
    """
    IP a consultar. Prioridad:
      1) argumento de linea de comandos  (python app.py 1.1.1.1)
      2) variable de entorno TARGET_IP
      3) valor por defecto 8.8.8.8 (DNS publico de Google, util para demos)
    """
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.getenv("TARGET_IP", "8.8.8.8")


# ---------------------------------------------------------------------------
# 2. CONSUMO DE LA API + MANEJO ROBUSTO DE ERRORES (>= 4 tipos)
# ---------------------------------------------------------------------------
def consultar_ipinfo(ip, token):
    """
    Realiza la peticion GET a ipinfo.io y devuelve el diccionario JSON.
    Maneja explicitamente multiples tipos de error y devuelve None si falla.
    """
    url = f"{API_HOST}/{ip}/json"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        respuesta = requests.get(url, headers=headers, timeout=TIMEOUT)

        # --- Errores por codigo de estado HTTP ---
        if respuesta.status_code == 200:
            return respuesta.json()                      # camino feliz
        elif respuesta.status_code in (401, 403):
            print(f"[ERROR 401/403] Token invalido o sin permisos para {ip}.")
        elif respuesta.status_code == 404:
            print(f"[ERROR 404] La IP '{ip}' no fue encontrada o es invalida.")
        elif respuesta.status_code == 429:
            print("[ERROR 429] Limite de peticiones excedido. Intente mas tarde.")
        else:
            print(f"[ERROR {respuesta.status_code}] Respuesta inesperada del servidor.")
        return None

    # --- Errores por excepcion (red, tiempo, formato) ---
    except requests.exceptions.Timeout:
        print(f"[ERROR Timeout] El servidor no respondio en {TIMEOUT} segundos.")
    except requests.exceptions.ConnectionError:
        print("[ERROR Conexion] No se pudo conectar a la API (revise su red/DNS).")
    except ValueError:
        print("[ERROR Formato] La respuesta no es un JSON valido.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR General] Fallo la peticion: {e}")
    return None


# ---------------------------------------------------------------------------
# 3. PROCESAMIENTO Y SALIDA (>= 3 campos)
# ---------------------------------------------------------------------------
def mostrar_informe(datos, ip):
    """Procesa el JSON y muestra un informe legible. Usa .get() para no
    reventar si un campo no viene en la respuesta."""
    print("=" * 55)
    print(f"  INFORME DE ENRIQUECIMIENTO DE IP: {ip}")
    print("=" * 55)
    print(f"  IP            : {datos.get('ip', 'N/D')}")
    print(f"  Hostname      : {datos.get('hostname', 'N/D')}")
    print(f"  Ciudad        : {datos.get('city', 'N/D')}")
    print(f"  Region        : {datos.get('region', 'N/D')}")
    print(f"  Pais          : {datos.get('country', 'N/D')}")
    print(f"  Organizacion  : {datos.get('org', 'N/D')}")   # ASN + ISP
    print(f"  Coordenadas   : {datos.get('loc', 'N/D')}")
    print(f"  Zona horaria  : {datos.get('timezone', 'N/D')}")
    print("=" * 55)


# ---------------------------------------------------------------------------
# 4. PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------
def main():
    token = obtener_token()
    ip = obtener_ip_objetivo()

    print(f"[INFO] Consultando ipinfo.io para la IP {ip} ...")
    datos = consultar_ipinfo(ip, token)

    if datos is None:
        # Hubo un error ya informado por consola -> salida distinta de 0
        sys.exit(2)

    mostrar_informe(datos, ip)
    print("[INFO] Consulta finalizada correctamente.")
    sys.exit(0)   # codigo de salida 0 = exito (lo exige el contenedor Docker)


if __name__ == "__main__":
    main()
