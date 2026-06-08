# IP Enrichment Tool — Enriquecimiento de IPs para análisis de seguridad

Herramienta de consola que, dada una dirección IP pública, consulta la API
externa **[ipinfo.io](https://ipinfo.io)** y devuelve un informe con la
geolocalización, el operador (ISP/ASN) y la zona horaria de esa IP. El proyecto
integra **consumo de API + Git + Docker + Jenkins (CI/CD)**.

## 1. Narrativa: Stakeholder y propuesta de valor

**Stakeholder:** un *analista de seguridad de red* que trabaja en un SOC/NOC.

**Problema:** cuando un sistema de detección (por ejemplo un NDR como Darktrace)
levanta una alerta por una conexión saliente hacia una IP pública desconocida,
el analista necesita saber **rápidamente quién es el dueño de esa IP**: en qué
país y ciudad está, qué organización/ISP la opera (su ASN) y su zona horaria.
Con esa información decide en segundos si la conexión es benigna (un CDN, un
proveedor cloud conocido) o sospechosa (un hosting en un país inesperado).
Hacer esta búsqueda manualmente para cada IP durante el triage de un incidente
es lento y propenso a errores.

**Solución:** esta herramienta hace **una consulta puntual** a ipinfo.io, procesa
la respuesta JSON y entrega un informe limpio por consola. Al estar
contenerizada con Docker, el analista puede ejecutarla en cualquier entorno sin
instalar dependencias, y al estar integrada en Jenkins se reconstruye de forma
automática y reproducible.

## 2. Datos procesados y manejo de errores

La aplicación procesa **8 campos** de la respuesta de la API (más de los 3
exigidos): `ip`, `hostname`, `city`, `region`, `country`, `org` (ASN + ISP),
`loc` (coordenadas) y `timezone`.

Maneja de forma robusta **más de 4 tipos de error**:

1. **Timeout** — el servidor no responde dentro del tiempo límite.
2. **Error de conexión** — no hay red o falla el DNS.
3. **Token inválido (401/403)** — la clave de API es incorrecta o no tiene permisos.
4. **IP no encontrada (404)** — la dirección no existe o tiene formato inválido.
5. **Límite excedido (429)** — se superó la cuota de peticiones.
6. **Respuesta malformada** — el cuerpo no es un JSON válido.

## 3. Guía de configuración (variables de entorno)

La clave de la API **nunca** está en el código. Se lee del sistema con la
librería `os`. Necesitas registrar una cuenta gratuita en ipinfo.io y copiar tu
token.

| Variable        | Obligatoria | Descripción                                  |
|-----------------|-------------|----------------------------------------------|
| `IPINFO_TOKEN`  | Sí          | Token de la API de ipinfo.io.                |
| `TARGET_IP`     | No          | IP a consultar (por defecto `8.8.8.8`).      |

Configuración:

```bash
# Linux / Bash (DEVASC VM)
export IPINFO_TOKEN="tu_token_aqui"
export TARGET_IP="8.8.8.8"
```

```powershell
# Windows (PowerShell)
$env:IPINFO_TOKEN = "tu_token_aqui"
$env:TARGET_IP = "8.8.8.8"
```

## 4. Instrucciones de ejecución

### Opción A — Automatizada con Docker (recomendada)

El script `build.sh` genera el Dockerfile, construye la imagen y ejecuta el
contenedor:

```bash
export IPINFO_TOKEN="tu_token_aqui"
bash ./build.sh
```

Resultado esperado: la app imprime el informe de la IP y el contenedor
`samplerunning` termina con estado `Exited (0)`. Se genera además
`evidencias/docker/output.txt`.

### Opción B — Manual (sin Docker, para probar el script)

```bash
pip install -r requirements.txt
export IPINFO_TOKEN="tu_token_aqui"
python3 app.py 8.8.8.8
```

## 5. Estructura del repositorio

```
.
├── app.py              # Script principal: consulta puntual a la API
├── build.sh            # Automatización: genera Dockerfile, build y run
├── requirements.txt    # Dependencias de Python (requests)
├── .gitignore          # Evita subir archivos sensibles (.env, etc.)
├── README.md
└── evidencias/
    ├── docker/
    │   ├── output.txt      # docker ps -a + logs con datos reales
    │   └── screenshot.png  # captura de la consola
    └── jenkins/
        ├── stage_view.png
        ├── console_output_build.png
        ├── credentials.png
        └── pipeline_script.txt
```

## 6. CI/CD con Jenkins

- **BuildAppJob** (estilo libre): clona este repositorio usando credenciales
  seguras almacenadas en Jenkins y ejecuta `bash ./build.sh`.
- **SamplePipeline** (pipeline, 2 etapas):
  - *Preparation*: detiene y elimina el contenedor previo (usa `catchError`
    para no fallar si no existe).
  - *Build*: ejecuta `BuildAppJob`.

El script del pipeline está en `evidencias/jenkins/pipeline_script.txt`.
