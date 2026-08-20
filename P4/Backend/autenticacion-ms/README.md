# Microservicio de autenticación

API REST en Go responsable del registro y acceso de usuarios. Es dueño exclusivo de la base de datos de autenticación.

El contrato OpenAPI se encuentra en `openapi.yaml` y puede importarse en Swagger Editor o Postman.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| POST | `/api/v1/auth/register` | Registra un lector y devuelve un JWT |
| POST | `/api/v1/auth/login` | Valida credenciales y devuelve un JWT |

### Registro

```json
{
  "nombre": "Ana",
  "apellido": "López",
  "correo": "ana@example.com",
  "password": "ClaveSegura123"
}
```

### Inicio de sesión

```json
{
  "correo": "ana@example.com",
  "password": "ClaveSegura123"
}
```

## Estructura

- `models`: entidades y errores del negocio.
- `schemas`: contratos de entrada de la API.
- `repository`: contratos y acceso a PostgreSQL.
- `service`: casos de uso y reglas de negocio.
- `controller`: entrada HTTP y respuestas JSON.
- `routes`: endpoints y middlewares.
- `security`: bcrypt y generación de JWT.
- `config`: lectura de variables de entorno.
- `cmd/api`: composición e inicio del servicio.

## Configuración

Copiar `.env.example` y proporcionar `DATABASE_URL` y un `JWT_SECRET` de al menos 32 caracteres. La migración inicial está en `migrations/001_init.sql`.

## Comandos

```bash
go mod tidy
go test ./...
go run ./cmd/api
```

El API Gateway será el único punto de entrada público. Este contenedor debe permanecer en la red interna de Docker Compose.
