# Microservicio de préstamos

Servicio en Python que administra préstamos y devoluciones. Es el segundo microservicio con GraphQL y utiliza MVC por capas.

## Endpoints

| Método | Ruta | Uso |
|---|---|---|
| POST | `/graphql` | Consultas y mutaciones de préstamos |
| POST | `/api/v1/prestamos/procesar-vencidos` | Procesamiento interno de vencimientos |
| GET | `/health` | Estado del servicio |

## Operaciones GraphQL

- `prestamo`
- `prestamosPorUsuario`
- `crearPrestamo`
- `devolverEjemplar`

```graphql
mutation {
  crearPrestamo(
    idUsuario: "b89bcb4d-a401-4a84-aef1-67fde55a0476"
    idsEjemplares: ["91ec04ee-319d-4620-a97c-c41f9221f4b1"]
    fechaLimite: "2026-09-01T23:59:00Z"
  ) {
    idPrestamo
    estado
    detalles { idDetalle idEjemplar estado }
  }
}
```

## Comunicación

- Préstamos llama a Catálogo mediante REST para marcar ejemplares como `PRESTADO` o `DISPONIBLE`.
- Al procesar vencimientos, llama directamente a Multas mediante REST HTTP/HTTPS.
- No utiliza RabbitMQ ni accede a las bases de datos de otros servicios.

Las URLs se configuran con `CATALOG_URL` y `FINES_URL`; pueden usar HTTPS cuando los servicios cuenten con certificados o un proxy TLS.

## MVC por capas

- `models`: entidades y estados.
- `schemas`: contratos REST adicionales.
- `repository`: contratos y persistencia PostgreSQL.
- `service`: creación, devolución, compensaciones y vencimientos.
- `controller`: GraphQL y REST.
- `routes`: registro de endpoints.
- `clients`: comunicación REST con Catálogo y Multas.
- `config`: variables de entorno.
