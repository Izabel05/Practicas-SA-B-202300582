### **Principios Solid**

**Principio de Resposabilidad Unica (SRP)**

Es un principio  que trata de que una clase tiene una aunica resposabilidad , esto en si significa que solo va a abar una cosa amenos que se trate de esa cosa no se puede cambiar o agregar codigo a esa clase.

Esto nos ayuda en que cuando quisieramos seguir expandiendo  una clase o un objeto al  seguir agregandole atributos  no tendriamos que tardar  en cambiar cada funcion o metodo que tenga que ver con esos atributos si no  al trabajar cada clase por separado y cada clase tratar una unica responsabilidad no tendriamos que estar tocando diferentes partes del codigo.

*Evidencia de applicacion en el codigo*
Archivo: app/exceptions/validation_exception.py

```py
from app.exceptions.aplication_exception import (
    ApplicationException,
)


class ValidationException(ApplicationException):
    """
    Indica que los datos recibidos no cumplen con las reglas
    de validación de la aplicación.
    """

    ERROR_CODE = "VALIDATION_ERROR"

    def __init__(
        self,
        errors: dict[str, str],
    ) -> None:
        super().__init__(
            message="Los datos proporcionados no son válidos.",
            error_code=self.ERROR_CODE,
            details={
                "fields": errors,
            },
        )

```
Esta clase es parte de este principio ya que tiene una unica responsabilidad la cual es : Representar una excepcion de validacion cuando los datos enviados por el usuario no cumplen las reglas de la aplicacion, como tal no valida datos , no genera respuestas HTTP, tampoco accede a la base de datos ni contiene reglas de negocio.

**Principio abierto-cerado (OCP)**

Este principio trata de que podemos seguir agregando codigo de manera continua a una clase , pero el codigo que vayamos a relizar en esta clase ya no se puede modificar.

Esto hace que como tal se deba plantear bien el tipo de funcionalidad de cada parte del codigo para que las funcionalidades no se repitan solo  por que no se puede modficar una y mejor se decide crear otra , eviatndo la duplicacion de codigo inecesario.

*Evidencia de applicacion en el codigo*
Archivo: app/services/solicitud_services.py


```py

class SolicitudService:
    """
    Gestiona los casos de uso relacionados con solicitudes
    operativas.
    """

    def __init__(
        self,
        repository: SolicitudRepositoryInterface,
    ) -> None:
        self._repository = repository
```
Esta clase como tal actualmente se le envia SolcitudServices, pero se podria realizar otra clase que siga de igual manera el contrato de solcitudrepositoryinterface y no alteraria el codigo que ya exite.

```py
class SolicitudRepository(SolicitudRepositoryInterface):
```
El servicio no depende de una implementación específica, sino de una interfaz (SolicitudRepositoryInterface). Esto permite extender la aplicación agregando nuevos repositorios sin modificar la lógica del servicio, cumpliendo así el principio Abierto/Cerrado.


**Principio de sustitucion de Liskov (LSP)**

Este principio habla de que se puede tener una clase y de esta clase haber subclases , al implementar este principio sin importar si se cambie la subclase por la clase el funcionamiento no deberia cambiar y no deberia alterar el codigo.

*Evidencia de applicacion en el codigo*
Archivo: app/exception/application_exception.py

```py
class ApplicationException(Exception):
```
se tiene esta clase  y estas que heredan de essa clase:

Aqui como se ve esta interfaz al respetar este contrato:
```py
class ValidationException(ApplicationException):

class SolicitudNotFoundException(ApplicationException):

class PersistenceException(ApplicationException):
```
Como tal estas excepciones pueden sustituir a ApplicationExceptions.Por ejemplo en el controlador esta lo siguiente:
```py
except ApplicationException as error:
    return self._crear_respuesta_error(error)
```
Este bloque puede manejar cualquiera de las siguientes excepciones:

* ValidationException
* SolicitudNotFoundException
* PersistenceException


Otro ejemplo seria cuando se lanza esto:
```py
raise ValidationException(errores)
```
El control no necesita hacer obligatoriamente esto:
```py
except ValidationException:
```
Puede hacer tambien esto:
```py
except ApplicationException as error:
```

Todas estas excepciones heredan de ApplicationException, por lo que pueden sustituirla sin modificar el comportamiento del controlador. Esto permite tratar diferentes tipos de errores utilizando una misma clase base, respetando el contrato definido por ApplicationException.


**Principio de Segregacion de Interfaces (ISP)**

Este preincipio habla de que  si se tiene una clase que es una interface y esta hereda sus funciones a otras clases , estas clases tienen la obligacion de usar todos los metodos que tenga la clase de la que heredaron sin excepciones.

Ya que de ocurrir una excepcion seria un error de diseño  y para esto es mejor tener en cuenta que  funciones o metodos de la clase siempre se usaran sin importar a quien hereden.

*Evidencia de applicacion en el codigo*
Archivo: app/repositories/solicitud_repository_interface.py

```py
class SolicitudRepositoryInterface(ABC):
    """
    Define el contrato de persistencia para las solicitudes.
    """

    @abstractmethod
    def crear(self, solicitud: Solicitud) -> Solicitud:
        pass

    @abstractmethod
    def obtener_todas(self) -> list[Solicitud]:
        pass

    @abstractmethod
    def obtener_por_id(
        self,
        solicitud_id: int,
    ) -> Solicitud | None:
        pass

    @abstractmethod
    def actualizar(
        self,
        solicitud: Solicitud,
    ) -> Solicitud | None:
        pass

    @abstractmethod
    def actualizar_estado(
        self,
        solicitud_id: int,
        estado: str,
    ) -> Solicitud | None:
        pass

    @abstractmethod
    def eliminar(
        self,
        solicitud_id: int,
    ) -> bool:
        pass

```
Aqui por ejemplo tenemos esta clase donde unicamente se encarga de las operaciones del repositorio de solicitudes , esto significa que no se encarga de cosas como: enviar_correo o generar_pdf , evitando asi tener que implementar esa clase de metodos cuando no se trabajan en solitud_repository por ejemplo:


```py

class SolicitudRepository(SolicitudRepositoryInterface):
    """
    Implementa las operaciones CRUD de la tabla solicitudes
    utilizando PostgreSQL.
    """

    def __init__(
        self,
        connection_factory: ConnectionFactory,
    ) -> None:
        self._connection_factory = connection_factory

    def crear(self, solicitud: Solicitud) -> Solicitud:
        consulta = """
            INSERT INTO solicitudes (
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado
            )
            VALUES (
                %(titulo)s,
                %(area_solicitante)s,
                %(prioridad)s,
                %(costo_estimado)s,
                %(estado)s
            )
            RETURNING
                id,
                titulo,
                area_solicitante,
                prioridad,
                costo_estimado,
                estado;
        """
...
```

**Principio de Inversion de Dependencias(DIP)**

Este principio trata de que al tener un sistema de bajo nivel que hace las implementaciones de un sistema de alto nivel , debe poder realizar las implementaciones tambien de otros sistemas de alto nivel por lo tanto no debe estar furtemente acoplado a un unico sistema ya que no se pordia utilizar en otras partes, para reutilizacion de codigo.

*Evidencia de aplicación*

Archivo: app/services/solicitud_service.py

```py
class SolicitudService:

    def __init__(
        self,
        repository: SolicitudRepositoryInterface,
    ):
        self._repository = repository
```

Aqui por ejemplo no dice *repository:solicitudrepository* dice *repository: SolicitudRepositoryInterface* por lo tanqto aqui service solo conoce el contrato y en main realiza lo siguiente:

```py
repository = SolicitudRepository(
    connection_factory=get_connection
)
```
y despues hacer esto:

```py
service = SolicitudService(
    repository=repository
)

```
Como tal el parametro repository crea un objeto de tipo SolicitudRepository pero como este mismo hereda de *SolicitudRepositoryInterface* entonces python entiende que el objeto cumple el contrato.

Esto se puede entender como el service dice quiero un repository que cumpla este contrato sin importar que repository sea.

El servicio únicamente conoce el contrato definido por SolicitudRepositoryInterface y no la implementación concreta. Esto permite sustituir el repositorio actual por otro diferente (por ejemplo, uno para pruebas, uno que utilice otra base de datos o uno en memoria) sin modificar la lógica del servicio.

Esta separación reduce el acoplamiento entre las capas de la aplicación y facilita el mantenimiento, las pruebas y la escalabilidad del sistema.