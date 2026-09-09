# Preguntas teoricas

## 1. Diferencia entre integracion continua y despliegue continuo

La integracion continua valida cada cambio mediante compilacion y pruebas automaticas para detectar errores temprano. El despliegue continuo toma un artefacto ya validado y actualiza un ambiente de ejecucion de forma automatizada. En este pipeline, los jobs de pruebas y build representan CI; la publicacion en GHCR y el despliegue con Helm representan CD.

## 2. Beneficios de automatizar pruebas y construccion de imagenes

La automatizacion hace repetible el proceso, reduce errores manuales y evita desplegar cambios que no compilan o no superan las pruebas. Ademas, la imagen identificada por el SHA permite relacionar exactamente un contenedor con el commit que lo produjo.

## 3. Funcion de un registro de contenedores

El registro conserva y distribuye imagenes versionadas. GHCR actua como punto de intercambio entre GitHub Actions, que construye y publica las imagenes, y GKE, que las descarga para ejecutar los microservicios.

## 4. Importancia del versionamiento en CI/CD

Las etiquetas por SHA son inmutables y permiten auditoria y rollback. La etiqueta `latest` facilita identificar la version mas reciente de `main`, mientras que los tags `v*` representan versiones deliberadamente seleccionadas para despliegue.

## 5. Manejo seguro de credenciales

Las conexiones de Neon se almacenan como Secrets de Kubernetes y no se escriben en Git. GitHub se autentica en GCP mediante OIDC y Workload Identity Federation, por lo que no existe una llave JSON permanente en el repositorio ni en GitHub Actions.
