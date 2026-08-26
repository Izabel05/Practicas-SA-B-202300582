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
- [Ambiente P4 Biblioteca - Local](<./Postman/P4 Biblioteca - Local.postman_environment.json>)

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

La colección puede importarse en Postman usando el formato Collection v2.1 incluido en el repositorio. El ambiente contiene la URL local del Gateway, datos de prueba y variables para conservar los identificadores generados durante la ejecución. Los tokens y los identificadores dinámicos se entregan vacíos y se completan mediante los scripts de Postman.

## Principios SOLID aplicados

Los microservicios utilizan una arquitectura MVC por capas que separa modelos, controladores, servicios y repositorios. Sobre esta organización se aplican los cinco principios SOLID para reducir el acoplamiento y facilitar las pruebas y el mantenimiento.

### 1. Principio de responsabilidad única (SRP)

Este principio indica que un componente debe encargarse de una sola responsabilidad y tener una única razón para cambiar. En el proyecto, los controladores reciben solicitudes, los servicios contienen las reglas de negocio y los repositorios administran la persistencia.

Un ejemplo concreto se encuentra en `Backend/autenticacion-ms/internal/security/bcrypt.go`. `BcryptHasher` solamente genera y compara hashes de contraseñas. No consulta usuarios, no crea tokens y no construye respuestas HTTP.

```go
type BcryptHasher struct {
    cost int
}

func (h BcryptHasher) Hash(password string) (string, error) {
    hash, err := bcrypt.GenerateFromPassword([]byte(password), h.cost)
    return string(hash), err
}

func (h BcryptHasher) Compare(hash, password string) error {
    return bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
}
```

Si cambia el algoritmo o el costo de protección de las contraseñas, el cambio se concentra en este componente sin modificar el controlador, el repositorio de usuarios o la generación de JWT.

### 2. Principio abierto/cerrado (OCP)

Este principio establece que un componente debe poder extenderse con nuevas implementaciones sin modificar su lógica principal. Autenticación define contratos para persistencia, protección de contraseñas y generación de tokens en `Backend/autenticacion-ms/internal/repository/interfaces.go`:

```go
type UserRepositoryContract interface {
    Create(ctx context.Context, user models.User, roleName string) (models.User, error)
    FindByEmail(ctx context.Context, email string) (models.User, error)
}

type PasswordHasher interface {
    Hash(password string) (string, error)
    Compare(hash, password string) error
}

type TokenGenerator interface {
    Generate(user models.User) (string, error)
}
```

`AuthService` trabaja con esos contratos y no con implementaciones concretas. Por ello se puede agregar otro repositorio, otro algoritmo de hash o una estrategia diferente de tokens proporcionando una implementación compatible, sin reescribir los casos de uso de registro e inicio de sesión.

### 3. Principio de sustitución de Liskov (LSP)

Este principio indica que una implementación debe poder sustituir a la abstracción que cumple sin alterar el funcionamiento esperado del componente que la utiliza.

`LoanService`, ubicado en `Backend/prestamos-ms/app/service/loan_service.py`, recibe objetos que cumplen los contratos `LoanRepository`, `CatalogClient` y `FineClient`. En producción utiliza `PostgresLoanRepository`, `HttpCatalogClient` y `HttpFineClient`; en las pruebas se sustituyen por implementaciones falsas.

```py
service = LoanService(
    FakeRepository(),
    FakeCatalogClient(),
    FakeFineClient(),
)
```

Por ejemplo, `FakeCatalogClient` conserva la operación definida por `CatalogClient`:

```py
class FakeCatalogClient:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.updates: list[tuple] = []

    def update_copy_status(self, copy_id, status):
        self.updates.append((copy_id, status))
```

El servicio puede trabajar con el cliente HTTP real o con el cliente falso porque ambos proporcionan el comportamiento acordado. Esto permite probar las reglas de préstamos sin depender de la red ni de que Catálogo esté ejecutándose.

### 4. Principio de segregación de interfaces (ISP)

Este principio recomienda crear interfaces pequeñas y enfocadas para que un componente no dependa de operaciones que no utiliza. En `Backend/prestamos-ms/app/repository/interfaces.py` las comunicaciones externas se separan en dos contratos:

```py
class CatalogClient(Protocol):
    def update_copy_status(self, copy_id: UUID, status: str) -> None: ...


class FineClient(Protocol):
    def create_fine(self, loan: Loan, days_overdue: int) -> None: ...
```

No se creó una interfaz general que mezclara todas las operaciones de Catálogo y Multas. `HttpCatalogClient` solamente está obligado a actualizar el estado de un ejemplar y `HttpFineClient` solamente a solicitar la creación de una multa. De esta manera, cada implementación depende únicamente de las operaciones que realmente necesita.

### 5. Principio de inversión de dependencias (DIP)

Este principio establece que la lógica de negocio no debe depender directamente de detalles de infraestructura; ambos deben depender de abstracciones. `LoanService` recibe sus dependencias por el constructor y utiliza los protocolos definidos por la aplicación:

```py
class LoanService:
    def __init__(
        self,
        repository: LoanRepository,
        catalog_client: CatalogClient,
        fine_client: FineClient,
    ) -> None:
        self._repository = repository
        self._catalog = catalog_client
        self._fines = fine_client
```

La lógica de crear, devolver o procesar un préstamo no conoce las consultas SQL de PostgreSQL ni los detalles de `httpx`. Solamente conoce las operaciones declaradas por los contratos. Las implementaciones concretas se construyen en `Backend/prestamos-ms/app/main.py`:

```py
app.state.loan_service = LoanService(
    PostgresLoanRepository(pool),
    HttpCatalogClient(runtime_settings.catalog_url),
    HttpFineClient(runtime_settings.fines_url),
)
```

Esta composición mantiene las reglas de negocio independientes de Neon, PostgreSQL y la biblioteca HTTP. También permite inyectar implementaciones falsas durante las pruebas unitarias.

### Conclusión sobre SOLID

La separación por capas asigna una responsabilidad concreta a cada componente. Los contratos permiten extender y sustituir implementaciones, las interfaces enfocadas evitan dependencias innecesarias y la inyección de dependencias mantiene la lógica de negocio separada de la infraestructura. Estas decisiones facilitan probar cada microservicio y modificar detalles técnicos sin reescribir sus casos de uso principales.

## Tecnologías utilizadas

| Componente | Tecnología | Responsabilidad |
| --- | --- | --- |
| API Gateway | Nginx | Punto de entrada y enrutamiento hacia los microservicios |
| Autenticación | Go, REST, JWT y bcrypt | Registro, inicio de sesión y emisión de tokens |
| Catálogo | Go, GraphQL y REST | Administración de categorías, autores, libros y ejemplares |
| Préstamos | Python, FastAPI y GraphQL | Creación, consulta, devolución y vencimiento de préstamos |
| Multas | Python, FastAPI y REST | Creación, consulta y pago de multas |
| Persistencia | PostgreSQL en Neon | Bases de datos persistentes separadas por servicio |
| Contenedores | Docker y Docker Compose | Construcción y ejecución conjunta del sistema |
| Contrato y pruebas | Postman | Documentación y validación manual de los endpoints |

## Estructura del proyecto

```text
P4/
├── Backend/
│   ├── api-gateway/          # Configuración de Nginx
│   ├── autenticacion-ms/     # Microservicio Go REST
│   ├── catalogo-ms/          # Microservicio Go GraphQL/REST
│   ├── prestamos-ms/         # Microservicio Python GraphQL/REST
│   ├── multas-ms/            # Microservicio Python REST
│   ├── .env                  # Configuración local, no se incluye en Git
│   └── docker-compose.yml    # Orquestación de los contenedores
├── Imagenes/                 # Diagramas y evidencias
├── Postman/                  # Colección y ambiente exportados
└── README.md
```

Cada microservicio mantiene sus modelos, controladores, servicios, repositorios, rutas, configuración y pruebas dentro de su propio directorio. Esta organización permite modificar o desplegar un servicio sin mezclar su código con el de los demás.

## Requisitos previos

Para ejecutar el sistema se necesita:

- Docker Desktop con Docker Compose.
- Un proyecto de Neon con acceso a PostgreSQL.
- Las cuatro bases de datos y sus migraciones iniciales.
- Postman Desktop, Postman Web o la extensión de Postman para VS Code.
- Conexión a Internet para acceder a Neon.

No es necesario instalar Go o Python en la computadora cuando el sistema se ejecuta con Docker, porque cada Dockerfile incluye el entorno requerido para construir y ejecutar su servicio.

## Configuración de las bases de datos en Neon

Dentro de un proyecto de Neon se utilizan cuatro bases independientes:

| Microservicio | Base de datos | Migración inicial |
| --- | --- | --- |
| Autenticación | `auth_db` | `Backend/autenticacion-ms/migrations/001_init.sql` |
| Catálogo | `catalog_db` | `Backend/catalogo-ms/migrations/001_init.sql` |
| Préstamos | `loan_db` | `Backend/prestamos-ms/migrations/001_init.sql` |
| Multas | `fine_db` | `Backend/multas-ms/migrations/001_init.sql` |

Para preparar la persistencia:

1. Crear el proyecto de Neon con Neon Auth desactivado, ya que la autenticación pertenece a `autenticacion-ms`.
2. Crear las cuatro bases indicadas en la tabla.
3. Seleccionar cada base en el SQL Editor de Neon.
4. Ejecutar el contenido de su archivo `001_init.sql` correspondiente.
5. Copiar la cadena de conexión de cada base conservando `sslmode=require`.
6. Colocar cada conexión en `Backend/.env`.

Cada servicio conoce únicamente su propia cadena de conexión. Los UUID de entidades externas se almacenan como referencias, pero no existen consultas ni claves foráneas entre bases de diferentes microservicios.

## Variables de entorno

El archivo local `Backend/.env` debe contener las siguientes variables:

```env
AUTH_DATABASE_URL=postgresql://usuario:password@host/auth_db?sslmode=require
CATALOG_DATABASE_URL=postgresql://usuario:password@host/catalog_db?sslmode=require
LOANS_DATABASE_URL=postgresql://usuario:password@host/loan_db?sslmode=require
FINES_DATABASE_URL=postgresql://usuario:password@host/fine_db?sslmode=require

JWT_SECRET=clave-aleatoria-de-al-menos-32-caracteres
JWT_DURATION_MINUTES=60
FINE_DAILY_RATE=5.00
```

`JWT_SECRET` se utiliza para firmar los tokens emitidos por Autenticación. Debe generarse de forma aleatoria, tener al menos 32 caracteres y mantenerse igual mientras se necesite validar los tokens existentes.

El archivo `.env` está excluido mediante `.gitignore` y no debe subirse al repositorio. Los archivos `.env.example` contienen únicamente nombres y valores de ejemplo; nunca deben incluir conexiones, contraseñas o secretos reales.

## Ejecución con Docker Compose

Desde la raíz del repositorio:

```powershell
cd P4\Backend
docker compose up --build
```

El comando construye las imágenes e inicia el Gateway y los cuatro microservicios. Para consultar el estado de los contenedores:

```powershell
docker compose ps
```

Para detener y retirar los contenedores:

```powershell
docker compose down
```

Docker Compose expone únicamente el API Gateway en `http://localhost:8080`. Los puertos `8081`, `8082`, `8083` y `8084` se utilizan dentro de la red de Docker y no constituyen puntos de entrada externos.

## Rutas del API Gateway

| Método | Ruta | Destino |
| --- | --- | --- |
| `GET` | `/health` | API Gateway |
| `GET` | `/health/auth` | Autenticación |
| `GET` | `/health/catalogo` | Catálogo |
| `GET` | `/health/prestamos` | Préstamos |
| `GET` | `/health/multas` | Multas |
| `POST` | `/api/v1/auth/register` | Autenticación |
| `POST` | `/api/v1/auth/login` | Autenticación |
| `POST` | `/catalogo/graphql` | Catálogo |
| `PATCH` | `/api/v1/ejemplares/{id}/estado` | Catálogo |
| `POST` | `/prestamos/graphql` | Préstamos |
| `POST` | `/api/v1/prestamos/procesar-vencidos` | Préstamos |
| `POST` | `/api/v1/multas` | Multas |
| `GET` | `/api/v1/multas/{id}` | Multas |
| `PATCH` | `/api/v1/multas/{id}/pagar` | Multas |
| `GET` | `/api/v1/usuarios/{id}/multas` | Multas |

Las operaciones GraphQL de Catálogo y Préstamos comparten una URL por servicio. La consulta o mutación que se ejecuta se define en el cuerpo de la solicitud.

## Orden de prueba en Postman

1. Seleccionar el ambiente `P4 Biblioteca - Local`.
2. Consultar los endpoints de estado.
3. Registrar un usuario o iniciar sesión con el usuario de prueba.
4. Crear una categoría.
5. Crear un autor.
6. Crear un libro utilizando los identificadores anteriores.
7. Crear un ejemplar para el libro.
8. Crear y consultar un préstamo.
9. Devolver un ejemplar o procesar préstamos vencidos.
10. Crear o consultar la multa asociada y posteriormente pagarla.

Los scripts de Postman guardan automáticamente en el ambiente los UUID y el token que necesitan las solicitudes posteriores. Para ejecutar todas las peticiones se puede utilizar la opción **Run Collection**.

## Evidencias de funcionamiento

### Contenedores iniciados

<!-- Agregar aquí la captura de `docker compose ps`. -->

Pendiente de agregar evidencia.

### Endpoints de estado

<!-- Agregar aquí la captura de las respuestas de los endpoints `/health`. -->

Pendiente de agregar evidencia.

### Ejecución de la colección de Postman

<!-- Agregar aquí la captura del resultado de `Run Collection`. -->

Pendiente de agregar evidencia.

## Conclusiones

La separación del sistema en cuatro microservicios permite que cada módulo mantenga sus propias reglas y datos. El API Gateway proporciona un único punto de entrada y evita exponer directamente los servicios internos.

GraphQL permite solicitar únicamente los campos requeridos en Catálogo y Préstamos, mientras que REST se utiliza para autenticación, operaciones internas y recursos con acciones concretas. La comunicación directa de Préstamos con Catálogo y Multas evita reenviar tráfico interno por el Gateway.

El uso de bases separadas reduce el acoplamiento de la persistencia, y Docker Compose permite construir y levantar todo el backend con un solo comando. Finalmente, la arquitectura por capas y la aplicación de SOLID facilitan las pruebas y el reemplazo de detalles de infraestructura sin modificar las reglas principales del sistema.
