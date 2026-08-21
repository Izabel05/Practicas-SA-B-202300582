# Práctica 4 - Biblioteca Digital

El proyecto implementa una biblioteca digital mediante cuatro microservicios: Autenticación, Catálogo, Préstamos y Multas. Los servicios se ejecutan en contenedores independientes, utilizan Go y Python, y reciben las solicitudes externas por medio de un API Gateway.

## Diagrama de arquitectura general

![Diagrama de arquitectura general](./Imagenes/image.png)

El diagrama muestra la separación funcional del sistema. El cliente consume el API Gateway, que actúa como punto de entrada y dirige cada solicitud al microservicio correspondiente:

- **Autenticación:** registro de usuarios e inicio de sesión mediante JWT.
- **Catálogo:** administración de categorías, autores, libros y ejemplares.
- **Préstamos:** creación, consulta y devolución de préstamos.
- **Multas:** creación, consulta y pago de multas.

Cada servicio administra su propia base de datos. Préstamos se comunica directamente con Catálogo para actualizar la disponibilidad de los ejemplares y con Multas para gestionar las multas relacionadas con préstamos vencidos. Estas comunicaciones internas son síncronas mediante HTTP/REST.

## Diagramas entidad-relación

Los diagramas ER representan el modelo persistente de cada microservicio. Las bases se mantienen separadas para evitar que un servicio consulte o modifique directamente las tablas pertenecientes a otro.

### Autenticación

![Diagrama ER de Autenticación](./Imagenes/image-1.png)

Contiene las entidades de usuarios y roles. Cada usuario pertenece a un rol y almacena la información necesaria para el registro, la autenticación y el control de su estado.

### Catálogo

![Diagrama ER de Catálogo](./Imagenes/image-2.png)

Modela categorías, autores, libros y ejemplares. Un libro pertenece a una categoría, puede tener varios autores mediante una relación muchos a muchos y puede disponer de varios ejemplares físicos con un estado de disponibilidad.

### Préstamos

![Diagrama ER de Préstamos](./Imagenes/image-3.png)

Separa la información general del préstamo de sus detalles. Un préstamo pertenece a un usuario y contiene uno o varios ejemplares, cada uno con su fecha de devolución y estado correspondiente.

### Multas

![Diagrama ER de Multas](./Imagenes/image-4.png)

Registra las multas generadas a partir de préstamos vencidos. Conserva los identificadores del préstamo y del usuario, el monto, el motivo, el estado y las fechas de generación y pago.

Los identificadores pertenecientes a otros servicios se almacenan como referencias UUID, pero no se implementan claves foráneas entre las diferentes bases de datos.

## Diagrama de implementación

![Diagrama de implementación](./Imagenes/Diagrama-implementacion.png)

El diagrama representa el despliegue del sistema mediante Docker Compose. El API Gateway utiliza Nginx y expone el puerto `8080`; los microservicios se ejecutan como contenedores internos independientes. Autenticación y Catálogo están implementados en Go, mientras que Préstamos y Multas están implementados en Python.

Las bases PostgreSQL se alojan externamente en Neon y cada microservicio utiliza una conexión independiente mediante PostgreSQL con TLS. La comunicación entre contenedores se realiza dentro de la red creada por Docker Compose.

La aplicación web o frontend mostrada en el diagrama es únicamente una representación visual de una posible ampliación futura. La entrega actual implementa solamente el backend y las solicitudes se prueban mediante Postman directamente contra el API Gateway.

## Contrato de microservicios

El contrato de los endpoints fue elaborado en Postman. La colección está organizada por microservicio e incluye las solicitudes REST y GraphQL necesarias para probar el sistema por medio del API Gateway.

- [Colección SA_P4_BibliotecaDigital](./Postman/SA_P4_BibliotecaDigital.postman_collection.json)

La colección contiene las siguientes carpetas:

| Carpeta | Operaciones documentadas |
| --- | --- |
| Auth | Estado del servicio, registro de usuario e inicio de sesión |
| Catálogo | Estado, categorías, autores, libros, ejemplares y disponibilidad |
| Préstamos | Estado, creación y consulta de préstamos, devoluciones y vencimientos |
| Multas | Estado, creación, consulta, listado por usuario y pago de multas |

Todas las solicitudes externas deben utilizar como URL base del Gateway:

```text
http://localhost:8080
```

La colección puede importarse en Postman usando el formato Collection v2.1 incluido en el repositorio.
