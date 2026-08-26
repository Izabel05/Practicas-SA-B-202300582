# Microservicio de multas

API REST en Python responsable de calcular, registrar, consultar y pagar multas. Usa MVC por capas y una base PostgreSQL privada.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/multas` | Registra una multa desde Préstamos |
| GET | `/api/v1/multas/{id}` | Consulta una multa |
| GET | `/api/v1/usuarios/{id}/multas` | Lista multas de un usuario |
| PATCH | `/api/v1/multas/{id}/pagar` | Paga una multa pendiente |
| GET | `/health` | Estado del servicio |

## Creación

```json
{
  "id_prestamo": "d08ea1d5-f786-4953-a17e-f08d751a65c4",
  "id_usuario": "edc4e05e-7268-4b67-b123-a7fa67544b20",
  "dias_atraso": 3,
  "fecha_generacion": "2026-08-20T18:00:00Z"
}
```

El monto se calcula como `dias_atraso × FINE_DAILY_RATE`. El valor predeterminado es `5.00`.

`id_prestamo` es único: si Préstamos repite la solicitud HTTPS, el servicio devuelve la multa existente y no duplica el cobro.

## MVC por capas

- `models`: entidad y estados de multa.
- `schemas`: solicitudes y respuestas REST.
- `repository`: contrato y persistencia PostgreSQL.
- `service`: cálculo y reglas de negocio.
- `controller`: controladores REST.
- `routes`: registro de endpoints.
- `config`: configuración externa.
