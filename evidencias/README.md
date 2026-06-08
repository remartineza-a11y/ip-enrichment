# Evidencias

Esta carpeta contiene las pruebas de que el flujo GitHub -> Docker -> Jenkins
funciona. Las imagenes (.png) debes capturarlas TU desde tu maquina virtual,
porque son capturas de pantalla de tu entorno real.

## /docker
- `output.txt`  -> Se genera SOLO al ejecutar `./build.sh`. Contiene la salida de
  `docker ps -a` (el contenedor `samplerunning` con estado `Exited (0)`) y los
  logs de la app con los datos REALES obtenidos de la API.
- `screenshot.png` -> Captura de la consola tras correr `./build.sh`, donde se ve
  el informe de la IP impreso por la app.

## /jenkins
- `pipeline_script.txt`        -> (ya incluido) El script del campo "Pipeline script".
- `stage_view.png`             -> Stage View de SamplePipeline con las 2 etapas
                                  (Preparation y Build) en VERDE.
- `console_output_build.png`   -> Console Output de BuildAppJob mostrando la
                                  construccion de la imagen y los datos reales de la API.
- `credentials.png`            -> Seccion Credentials de Jenkins con el token de
                                  GitHub configurado (no visible en texto plano).
