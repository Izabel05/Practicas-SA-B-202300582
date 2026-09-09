# Lista de evidencias

Agregar aqui las capturas de la ejecucion final sin mostrar credenciales.

1. Pull request con los jobs de pruebas en estado exitoso.
2. Matriz con la construccion exitosa de las seis imagenes.
3. Paquetes publicos visibles en GitHub Container Registry.
4. Ejecucion del tag `v*` con el job `Desplegar en GKE` exitoso.
5. Salida de `kubectl get pods,services,cronjobs -n sa-p6`.
6. Aplicacion accesible mediante la IP publica del `api-gateway`.
7. Historial de ejecuciones de GitHub Actions.

Convencion sugerida:

```text
01-pr-pruebas.png
02-build-imagenes.png
03-ghcr-publico.png
04-deploy-gke.png
05-recursos-kubernetes.png
06-api-gateway.png
```
