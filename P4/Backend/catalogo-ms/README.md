# Microservicio de catálogo

Servicio en Go que administra categorías, autores, libros y ejemplares. Utiliza GraphQL para el catálogo y REST para la comunicación interna con Préstamos.

El contrato GraphQL está documentado en `schema.graphql`; el contrato REST interno está en `openapi.yaml`.

## Endpoints

| Método | Ruta | Uso |
|---|---|---|
| POST | `/graphql` | Consultas y mutaciones GraphQL |
| PATCH | `/api/v1/ejemplares/{id}/estado` | Actualización interna de disponibilidad |
| GET | `/health` | Estado del servicio |

## Ejemplo GraphQL

```graphql
query {
  libros {
    id_libro
    titulo
    categoria { nombre }
    autores { nombre apellido }
    ejemplares { id_ejemplar codigo_inventario estado }
  }
}
```

```graphql
mutation {
  crearCategoria(nombre: "Arquitectura", descripcion: "Libros de software") {
    id_categoria
    nombre
  }
}
```

Las mutaciones disponibles son `crearCategoria`, `crearAutor`, `crearLibro`, `crearEjemplar` y `actualizarEstadoEjemplar`.

## MVC por capas

- `models`: entidades del catálogo.
- `schemas`: solicitudes REST.
- `repository`: contratos y persistencia PostgreSQL.
- `service`: validaciones y reglas de catálogo.
- `controller`: controladores GraphQL y REST.
- `routes`: endpoints y middleware.
- `config`: variables de entorno.

La base de Catálogo es privada: ningún otro microservicio consulta sus tablas directamente.
