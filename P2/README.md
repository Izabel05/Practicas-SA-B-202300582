# Tecnologías y seguridad de la aplicación

El proyecto implementa un sistema web de registro, autenticación y autorización por roles. Está dividido en un frontend desarrollado con React y un backend que expone una API REST con FastAPI.

## Tecnologías utilizadas

| Área | Tecnología | Uso dentro del proyecto |
| --- | --- | --- |
| Frontend | React 19 y TypeScript | Formularios de registro e inicio de sesión, página principal y manejo del estado del usuario. |
| Construcción | Vite | Servidor de desarrollo y generación del frontend. |
| Comunicación HTTP | Axios | Peticiones a la API, envío automático de cookies y reintento de solicitudes después de renovar la sesión. |
| Backend | Python y FastAPI | Endpoints REST, validación de peticiones, inyección de dependencias y manejo global de errores. |
| Validación | Pydantic | Validación y normalización de los datos de registro, login y respuesta. |
| Base de datos | PostgreSQL | Almacenamiento de usuarios, roles, contraseñas protegidas y fechas de acceso. |
| Acceso a datos | Psycopg 3 y psycopg-pool | Consultas SQL, transacciones y grupo de conexiones con PostgreSQL. |
| Contraseñas | Argon2id | Creación y verificación de hashes de contraseñas. |
| Autenticación | PyJWT | Creación, validación y renovación de tokens JWT firmados. |
| Sesión | Cookies HttpOnly | Transporte del JWT entre el navegador y el backend. |

## JSON Web Token (JWT)

La autenticación se implementa en `Backend/app/service/jwt_service.py` mediante `JWTService`. Cuando las credenciales son correctas, `LoginService` solicita la creación de un token que contiene los siguientes *claims*:

```py
payload = {
    "sub": str(user_id),
    "role": role.value,
    "iat": now,
    "exp": expiration,
    "iss": Settings.JWT_ISSUER,
    "aud": Settings.JWT_AUDIENCE,
}
```

- `sub` identifica al usuario autenticado.
- `role` se utiliza para autorizar el acceso a las rutas según el rol `ADMIN` o `CLIENTE`.
- `iat` indica cuándo se emitió el token.
- `exp` establece su fecha de expiración.
- `iss` identifica al emisor.
- `aud` identifica al cliente para el cual fue generado.

El token se firma con la clave privada de configuración y con el algoritmo indicado por `JWT_ALGORITHM`, cuyo valor predeterminado es `HS256`:

```py
return jwt.encode(
    payload=payload,
    key=Settings.JWT_SECRET_KEY,
    algorithm=Settings.JWT_ALGORITHM,
)
```

Al acceder a `/api/protected/ruta-1` o `/api/protected/ruta-2`, la dependencia `get_current_user` obtiene el JWT de la cookie y solicita su validación. `JWTService.validate_token()` comprueba la firma, la expiración, el emisor y la audiencia. Después, `require_roles()` verifica si el rol incluido en el token tiene permiso para utilizar la ruta.

El sistema también define una ventana de renovación. Cuando Axios recibe un `401` de una ruta que no sea login, registro o renovación, el interceptor de `Frontend/app/src/services/api.tsx` llama a `POST /api/auth/refresh`. El backend valida la firma del token expirado y, si todavía se encuentra dentro de `JWT_RENEWAL_WINDOW_SECONDS`, genera un JWT nuevo y reemplaza la cookie. Finalmente, Axios repite la solicitud original una sola vez.

## Protección de contraseñas con Argon2id

Las contraseñas no se almacenan en texto plano ni se cifran con un algoritmo reversible. `Backend/app/service/password_service.py` utiliza `PasswordHasher` de `argon2-cffi` para generar un hash Argon2id durante el registro:

```py
def hash_password(self, password: str) -> str:
    return self._password_hasher.hash(password)
```

Durante el inicio de sesión se compara la contraseña recibida con el hash almacenado:

```py
return self._password_hasher.verify(
    password_hash,
    password,
)
```

Se eligió hashing para las contraseñas porque no es necesario recuperar su valor original. Si la base de datos se expone, el sistema no contiene una clave con la que puedan descifrarse directamente todas las contraseñas.


## Cookies de autenticación

`Backend/app/service/cookie_service.py` guarda el JWT en una cookie cuyo nombre predeterminado es `access_token`. El backend la configura de la siguiente manera:

```py
response.set_cookie(
    key=Settings.COOKIE_NAME,
    value=token,
    max_age=cookie_lifetime,
    httponly=True,
    secure=Settings.COOKIE_SECURE,
    samesite=Settings.COOKIE_SAMESITE,
    path=Settings.COOKIE_PATH,
)
```

Las opciones cumplen estas funciones:

- `HttpOnly`: impide que JavaScript del navegador lea directamente el JWT y reduce su exposición ante ataques XSS.
- `Secure`: cuando se activa, la cookie solamente se transmite mediante HTTPS. Puede estar desactivada durante el desarrollo local, pero debe activarse en producción.
- `SameSite`: limita el envío de la cookie en solicitudes originadas desde otros sitios y ayuda a reducir ataques CSRF. El valor predeterminado del proyecto es `lax`.
- `Path=/`: permite enviar la cookie a las rutas de toda la API.
- `Max-Age`: conserva la cookie durante la vigencia del JWT más la ventana permitida para renovarlo.

Axios utiliza `withCredentials: true` en `Frontend/app/src/services/api.tsx`, por lo que el navegador incluye la cookie en las peticiones a la API:

```ts
export const api = axios.create({
  baseURL: apiUrl,
  withCredentials: true,
});
```

En el logout, `LoginController` utiliza `CookieService.delete_auth_cookie()` para ordenar al navegador que elimine la cookie. Como el token se almacena en una cookie HttpOnly, el frontend guarda en `sessionStorage` solamente los datos públicos necesarios para mostrar la interfaz, no el JWT.

# Diagrama de secuencias

![alt text](<Diagrama_actividades - Diagrama de Secuencia (1).png>)



# Principios SOLID aplicados en el backend

El backend aplica los principios SOLID mediante una arquitectura separada en rutas, controladores, servicios, repositorios e interfaces. A continuación se explica dónde se observa cada principio y por qué se tomó esa decisión.

## 1. Principio de responsabilidad única (SRP)

Este principio establece que una clase o módulo debe tener una sola responsabilidad y, por lo tanto, una sola razón para cambiar.

En el backend se aplica mediante la separación de responsabilidades por capas y servicios especializados:

- `Backend/app/routes/auth_routes.py` solamente define las rutas HTTP de autenticación, sus códigos de respuesta y las dependencias que necesita cada endpoint.
- `Backend/app/controller/login_controller.py` coordina la petición de inicio o cierre de sesión y la escritura o eliminación de la cookie, pero delega la lógica de autenticación.
- `Backend/app/service/login_service.py` contiene únicamente el caso de uso de inicio de sesión: busca al usuario, valida su estado y contraseña, genera el token y actualiza el último acceso.
- `Backend/app/service/password_service.py` se ocupa exclusivamente de generar y verificar hashes de contraseñas con Argon2.
- `Backend/app/service/jwt_service.py` se ocupa de crear, validar y renovar tokens JWT.
- `Backend/app/service/cookie_service.py` administra exclusivamente la cookie de autenticación.
- `Backend/app/repository/user_repository.py` concentra el acceso y mapeo de los datos de usuarios en PostgreSQL.

La decisión evita que una ruta o un controlador concentre validación HTTP, reglas de negocio, seguridad y consultas SQL. Por ejemplo, si cambia el algoritmo para proteger contraseñas, el cambio queda localizado en `PasswordService`; si cambia la forma de persistir usuarios, se modifica `UserRepository` sin alterar el flujo de inicio de sesión.

### Evidencia de aplicación

Archivo: `Backend/app/service/password_service.py`

```py
class PasswordService(PasswordServiceInterface):
    """Genera y verifica hashes Argon2id."""

    def __init__(self) -> None:
        self._password_hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self._password_hasher.hash(password)

    def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        # Verificación del hash de la contraseña
        ...
```

Esta clase tiene una única responsabilidad: proteger y verificar contraseñas. No consulta usuarios, no crea tokens, no administra cookies y no genera respuestas HTTP. Por ello, un cambio de Argon2 o de la política de hash afecta a esta clase y no al resto del flujo de autenticación.

## 2. Principio abierto/cerrado (OCP)

Este principio indica que los componentes deben estar abiertos a la extensión, pero cerrados a la modificación.

Se observa en las abstracciones:

- `Backend/app/service/interfaces/password_service_interface.py` define el contrato para generar y verificar hashes.
- `Backend/app/service/interfaces/token_service_interface.py` define el contrato para crear, validar y renovar tokens.
- `Backend/app/repository/interface/user_repository_interface.py` y `Backend/app/repository/interface/role_repository_interface.py` definen las operaciones de persistencia que necesitan los casos de uso.
- `Backend/app/service/password_service.py`, `Backend/app/service/jwt_service.py`, `Backend/app/repository/user_repository.py` y `Backend/app/repository/role_repository.py` son implementaciones concretas de esos contratos.

Gracias a esta decisión es posible extender el sistema con otra implementación, por ejemplo un servicio de tokens opacos, otro algoritmo de hash o un repositorio basado en otra tecnología, manteniendo el mismo contrato. Los casos de uso `LoginService`, `RegistroService` y `RefreshTokenService` no tendrían que modificar su lógica; solamente habría que proporcionar la nueva implementación en `Backend/app/dependencies/auth_dependencie.py`.

### Evidencia de aplicación

Archivo: `Backend/app/service/interfaces/token_service_interface.py`

```py
class TokenServiceInterface(ABC):
    @abstractmethod
    def create_token(
        self,
        user_id: UUID,
        role: RoleName,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def validate_token(self, token: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def renew_token(self, expired_token: str) -> str:
        raise NotImplementedError
```

Archivo: `Backend/app/service/jwt_service.py`

```py
class JWTService(TokenServiceInterface):
    """Genera, valida y renueva tokens JWT."""

    def create_token(
        self,
        user_id: UUID,
        role: RoleName,
    ) -> str:
        ...
```

El contrato permanece estable y `JWTService` es una implementación concreta. Si en el futuro se crea, por ejemplo, `OpaqueTokenService(TokenServiceInterface)`, se puede agregar esa capacidad y cambiar la implementación inyectada sin modificar la lógica interna de `LoginService` o `RefreshTokenService`. El sistema queda abierto a nuevas estrategias de token y cerrado a cambios innecesarios en los casos de uso existentes.

## 3. Principio de sustitución de Liskov (LSP)

Este principio establece que una implementación concreta debe poder sustituir a su abstracción sin alterar el funcionamiento esperado del sistema.

En el código:

- `JWTService` hereda de `TokenServiceInterface` e implementa `create_token`, `validate_token` y `renew_token` respetando sus firmas y tipos de retorno.
- `PasswordService` hereda de `PasswordServiceInterface` e implementa `hash_password` y `verify_password`.
- `UserRepository` y `RoleRepository` implementan todos los métodos definidos por `UserRepositoryInterface` y `RoleRepositoryInterface`, respectivamente.

Por ejemplo, `LoginService` recibe un `TokenServiceInterface` y utiliza `create_token` sin depender de que el objeto sea específicamente un `JWTService`. Cualquier otra clase que cumpla correctamente ese contrato puede ocupar su lugar sin cambiar el caso de uso. La misma sustitución es posible con el servicio de contraseñas y los repositorios.

La decisión facilita reemplazar implementaciones y crear dobles de prueba, siempre que conserven el comportamiento indicado por la interfaz: los métodos deben aceptar los mismos datos, devolver los tipos acordados y comunicar los errores de forma compatible.

### Evidencia de aplicación

Archivo: `Backend/app/service/login_service.py`

```py
class LoginService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
        token_service: TokenServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    def execute(self, schema: LoginSchema) -> LoginResult:
        ...
        token = self._token_service.create_token(
            user_id=user.id,
            role=user.role_name,
        )
```

Archivo: `Backend/app/service/jwt_service.py`

```py
class JWTService(TokenServiceInterface):
    def create_token(
        self,
        user_id: UUID,
        role: RoleName,
    ) -> str:
        ...
```

`LoginService` trabaja con el tipo base `TokenServiceInterface`, mientras que `JWTService` respeta ese contrato. Por eso el objeto concreto puede sustituirse por otra implementación compatible: `LoginService` seguirá enviando un identificador y un rol y seguirá recibiendo un token de tipo `str`, sin necesitar condiciones especiales para saber qué implementación está utilizando.

## 4. Principio de segregación de interfaces (ISP)

Este principio indica que un componente no debe depender de operaciones que no necesita. Es preferible tener contratos enfocados en una capacidad concreta en lugar de una única interfaz general para todo el sistema.

Esto se aplica al dividir los contratos según su área de responsabilidad:

- `PasswordServiceInterface` contiene solamente operaciones de contraseñas.
- `TokenServiceInterface` contiene solamente operaciones relacionadas con tokens.
- `RoleRepositoryInterface` expone únicamente `find_by_name`, que es la consulta de roles requerida por el registro.
- `UserRepositoryInterface` agrupa únicamente las operaciones de usuarios utilizadas por los casos de uso actuales.

Así, `RegistroService` depende de las interfaces de usuarios, roles y contraseñas, pero no de operaciones JWT; `RefreshTokenService` depende del contrato de tokens, pero no de repositorios ni del servicio de contraseñas. Esta separación reduce el acoplamiento y evita obligar a las implementaciones a definir métodos ajenos a su propósito.

### Evidencia de aplicación

Archivo: `Backend/app/repository/interface/role_repository_interface.py`

```py
class RoleRepositoryInterface(ABC):
    """Define las operaciones necesarias para consultar roles."""

    @abstractmethod
    def find_by_name(
        self,
        role_name: RoleName,
    ) -> Role | None:
        raise NotImplementedError
```

Archivo: `Backend/app/service/interfaces/password_service_interface.py`

```py
class PasswordServiceInterface(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        raise NotImplementedError
```

En lugar de crear una interfaz general que mezcle usuarios, roles, tokens y contraseñas, se definieron contratos separados por capacidad. Como resultado, `RoleRepository` solamente está obligado a implementar consultas de roles y `PasswordService` solamente operaciones relacionadas con contraseñas; ninguno debe implementar métodos que no le corresponden.

## 5. Principio de inversión de dependencias (DIP)

Este principio establece que la lógica de alto nivel no debe depender directamente de detalles de infraestructura; ambos deben depender de abstracciones.

Los casos de uso aplican este principio mediante inyección por constructor:

- `LoginService` depende de `UserRepositoryInterface`, `PasswordServiceInterface` y `TokenServiceInterface`, no de PostgreSQL, Argon2 o JWT directamente.
- `RegistroService` depende de `UserRepositoryInterface`, `RoleRepositoryInterface` y `PasswordServiceInterface`.
- `RefreshTokenService` depende de `TokenServiceInterface`.

Los detalles concretos se crean y conectan en `Backend/app/dependencies/auth_dependencie.py`. Por ejemplo, `get_login_service()` inyecta `UserRepository`, `PasswordService` y `JWTService` en `LoginService`, mientras que FastAPI inyecta los controladores en las rutas mediante `Depends`.

La razón de esta decisión es mantener la lógica de negocio independiente de frameworks y bibliotecas específicas. `LoginService` sabe que puede buscar un usuario, verificar una contraseña y crear un token, pero no necesita conocer las consultas SQL, Argon2 ni la biblioteca utilizada para codificar JWT. Esto mejora la mantenibilidad, permite sustituir infraestructura y hace más sencillas las pruebas unitarias mediante implementaciones simuladas de las interfaces.

### Evidencia de aplicación

Archivo: `Backend/app/service/login_service.py`

```py
class LoginService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
        token_service: TokenServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service
```

Archivo: `Backend/app/dependencies/auth_dependencie.py`

```py
def get_login_service() -> LoginService:
    return LoginService(
        user_repository=get_user_repository(),
        password_service=get_password_service(),
        token_service=get_token_service(),
    )
```

El módulo de alto nivel `LoginService` solicita objetos que cumplan interfaces y no construye directamente `UserRepository`, `PasswordService` o `JWTService`. Las implementaciones concretas se conectan fuera del caso de uso, en el módulo de dependencias. Así se invierte el control de la creación de objetos y se evita que la lógica de inicio de sesión quede fuertemente acoplada a PostgreSQL, Argon2 o JWT.

## Conclusión

La aplicación conjunta de SOLID hace que cada componente tenga un propósito delimitado, que las implementaciones puedan extenderse o reemplazarse mediante contratos y que la lógica de autenticación no quede acoplada a los detalles técnicos. En este backend, la evidencia principal se encuentra en la separación por capas, las interfaces abstractas y la composición centralizada de dependencias.
