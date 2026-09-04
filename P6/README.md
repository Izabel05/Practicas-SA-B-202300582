# Práctica 6 - Despliegue en Google Kubernetes Engine

Esta carpeta adapta la plataforma de la Práctica 5 para desplegarla en un clúster administrado de GKE con un nodo, imágenes privadas en Artifact Registry, PostgreSQL externo en tres instancias de Neon, RabbitMQ con almacenamiento persistente y un `LoadBalancer` público para el API Gateway. Aunque el PDF indica dos nodos, esta configuración sigue la indicación posterior de usar uno para no consumir rápidamente los créditos.

No se crean cuentas, proyectos ni bases de Neon desde estos archivos. Las cadenas de conexión terminan almacenadas como Secrets de Kubernetes y los Deployments las inyectan en los contenedores. No se necesita un archivo `.env` para GKE; el script recibe los valores temporalmente desde la sesión de PowerShell para evitar escribir credenciales en Git.

## Arquitectura preparada

- GKE zonal con un nodo `e2-standard-2` para reducir el consumo de créditos.
- Artifact Registry privado con seis imágenes: gateway, cuatro microservicios y worker de cronjobs.
- Cinco bases lógicas distribuidas entre tres instancias/proyectos de Neon.
- `Dockerfile.prod` multi-stage para cada imagen propia, con una etapa final mínima y usuario sin privilegios.
- RabbitMQ dentro del clúster, con PVC atendido por la StorageClass predeterminada de GKE.
- API Gateway publicado mediante `Service` de tipo `LoadBalancer`.
- Comunicación asíncrona `prestamos-ms -> RabbitMQ -> multas-ms` para solicitar multas, más productor/consumidor de resúmenes de cronjobs.
- NetworkPolicies con DNS, tráfico interno controlado, acceso público al gateway y salida TCP 5432 hacia Neon.

## Requisitos locales

Instale y autentique `gcloud`, Docker, `kubectl` y Helm. Debe contar con un proyecto de Google Cloud con facturación o créditos habilitados. Antes de ejecutar comandos, confirme el proyecto activo con `gcloud config get-value project`.

## 1. Crear las bases en Neon

Cree manualmente tres instancias o proyectos de Neon y distribuya las bases así:

| Instancia de Neon | Bases de datos |
|---|---|
| Neon 1 | `auth_db`, `catalogo_db` |
| Neon 2 | `prestamos_db`, `multas_db` |
| Neon 3 | `cronjobs_db` |

Cada microservicio conserva una URL propia, aunque dos URL puedan compartir el mismo host de Neon. Use URLs con `sslmode=require` y no las guarde en archivos versionados.

En PowerShell cargue las variables únicamente en la sesión actual:

```powershell
$env:AUTH_DATABASE_URL="postgresql://.../auth_db?sslmode=require"
$env:CATALOG_DATABASE_URL="postgresql://.../catalogo_db?sslmode=require"
$env:LOANS_DATABASE_URL="postgresql://.../prestamos_db?sslmode=require"
$env:FINES_DATABASE_URL="postgresql://.../multas_db?sslmode=require"
$env:CRONJOBS_DATABASE_URL="postgresql://.../cronjobs_db?sslmode=require"
$env:JWT_SECRET="una-cadena-aleatoria-de-32-o-mas-caracteres"
```

Inicialice las tablas después de crear las bases (requiere `psql`):

```powershell
.\P6\scripts\00-init-neon.ps1
```

## 2. Configurar Google Cloud y crear el clúster

Los comandos son deliberadamente parametrizados: reemplace `MI_PROYECTO` y ajuste región o zona si corresponde.

```powershell
.\P6\scripts\01-configure-gcp.ps1 -ProjectId MI_PROYECTO
```

El script habilita las API necesarias, crea un repositorio privado de Artifact Registry si falta, crea un clúster zonal de un nodo y configura `kubectl`. Revise la cuota y el costo mostrado por Google antes de mantener el clúster activo.

## 3. Construir y publicar imágenes

```powershell
.\P6\scripts\02-build-push.ps1 -ProjectId MI_PROYECTO
```

El código fuente se toma de `P4/Backend`; no se duplica dentro de P6. El worker se toma de `P6/cronjobs/cronjob2`. El script construye explícitamente cada `Dockerfile.prod` multi-stage y publica la imagen en Artifact Registry; no configura acceso público.

## 4. Crear Secrets y desplegar

```powershell
.\P6\scripts\03-create-secrets.ps1
.\P6\scripts\04-deploy.ps1 -ProjectId MI_PROYECTO
```

Compruebe el resultado:

```powershell
kubectl get nodes -o wide
kubectl -n sa-p6 get pods
kubectl -n sa-p6 get pvc
kubectl -n sa-p6 get service api-gateway
```

La IP externa puede tardar unos minutos. Cuando aparezca, pruebe `http://IP_EXTERNA/health` y luego los endpoints del archivo `P4/Postman/SA_P4_BibliotecaDigital.postman_collection.json`.

## 5. Evidencias

Ejecute:

```powershell
.\P6\scripts\05-evidence.ps1
```

Complete la lista de `evidencias/README.md` con capturas de consola, pods, registro, almacenamiento, IP pública y peticiones reales. No capture ni ejecute `kubectl get secret -o yaml`, porque expondría credenciales.

## Respuestas teóricas

### 1. ¿Qué es un clúster administrado y en qué difiere de uno local?

En un clúster administrado, el proveedor opera el plano de control de Kubernetes, integra identidad, red, almacenamiento y actualizaciones, y ofrece disponibilidad y observabilidad propias de la nube. Un clúster local simula gran parte de esos recursos en una sola computadora y normalmente no proporciona balanceadores, discos ni direcciones públicas reales. En GKE todavía debemos dimensionar los nodos, desplegar y asegurar las cargas y vigilar el consumo.

### 2. ¿Qué es un Service LoadBalancer y cómo lo implementa GCP?

Es un Service que solicita al proveedor un balanceador externo y una dirección IP pública. GKE observa el objeto de Kubernetes, crea los recursos de red de Google Cloud y dirige el tráfico al puerto del Service y después a los pods seleccionados. Aquí el tráfico público llega al API Gateway por el puerto 8080; los microservicios permanecen como `ClusterIP`.

### 3. ¿Qué es un registro de contenedores y por qué se necesita?

Es un repositorio remoto y versionado de imágenes OCI. Los nodos de GKE no pueden usar las imágenes que solo existen en la computadora de desarrollo; deben descargarlas desde un registro accesible. Artifact Registry centraliza las etiquetas, permisos y análisis de las imágenes usadas por el despliegue.

### 4. ¿Qué administra el proveedor y qué administra el estudiante?

GKE administra el plano de control, su disponibilidad y la integración con balanceadores y discos. El estudiante administra los nodos y su tamaño, imágenes, Deployments, Services, Secrets, políticas de red, bases externas, actualizaciones de la aplicación, copias de seguridad, observabilidad y costos. El modo administrado reduce trabajo operativo, pero no transfiere la seguridad ni la confiabilidad de la aplicación al proveedor.

### 5. ¿Qué costos se generan y cómo se reducen?

El costo real combina cómputo de un nodo, discos persistentes, balanceador/IP pública, almacenamiento y transferencia de Artifact Registry, tráfico saliente y el plan elegido en Neon. Registre en la entrega el valor observado en Billing durante el intervalo de la práctica; no use una cifra fija porque tarifas, créditos, región y horas activas varían. Para reducirlo: use el clúster zonal de un nodo indicado, imágenes compactas, límites de recursos, la capa gratuita de Neon y elimine el clúster y el registro al terminar.

## Limpieza obligatoria

```powershell
.\P6\scripts\99-destroy.ps1 -ProjectId MI_PROYECTO -DeleteArtifactRepository
```

Verifique además en la consola que no queden discos, direcciones IP, balanceadores ni recursos facturables. Neon se elimina desde su propia consola si ya no se utilizará. Tome una captura de la eliminación para la evidencia final.

## Datos que debe completar antes de entregar

- Proyecto, región y zona usados.
- Dirección IP pública o dominio.
- Fecha y duración del despliegue.
- Costo aproximado observado en Billing y costo de Neon.
- Capturas solicitadas en `evidencias/README.md`.
- Confirmación y evidencia de la limpieza final.
