### Primer Promt:
Estoy realizando una base de datos relacional utilizando PostgresSQL , alojada de manera persistente en NeonDB .Necesito que me ayudes a diseñar el esquema de la base de datos con buenas practicas de PostgresSQL , ademas de aplicar sus respectivas restricciones de (primary key,not null, etc). Teniendo en cuenta los siguientes campòs Id: Entero Titulo:string area?solictante: string prioridad:entero (entre 1 y 5 ) costo_estimado: decimal estado: string

![alt text](image.png)

#### Respuesta Obtenida:

Para este caso, puedes crear una tabla llamada solicitudes aplicando restricciones para garantizar que los datos sean válidos y consistentes.

Esquema recomendado
```
CREATE TABLE solicitudes (
    id INTEGER GENERATED ALWAYS AS IDENTITY,

    titulo VARCHAR(150) NOT NULL,

    area_solicitante VARCHAR(100) NOT NULL,

    prioridad SMALLINT NOT NULL,

    costo_estimado NUMERIC(12, 2) NOT NULL DEFAULT 0.00,

    estado VARCHAR(20) NOT NULL DEFAULT 'registrada',

    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_solicitudes
        PRIMARY KEY (id),

    CONSTRAINT chk_solicitudes_titulo
        CHECK (LENGTH(TRIM(titulo)) >= 3),

    CONSTRAINT chk_solicitudes_area
        CHECK (LENGTH(TRIM(area_solicitante)) >= 2),

    CONSTRAINT chk_solicitudes_prioridad
        CHECK (prioridad BETWEEN 1 AND 5),

    CONSTRAINT chk_solicitudes_costo
        CHECK (costo_estimado >= 0),

    CONSTRAINT chk_solicitudes_estado
        CHECK (
            estado IN (
                'registrada',
                'en_proceso',
                'finalizada',
                'cancelada'
            )
        )
);
```
Explicación de los campos

| Campo                 | Tipo de dato       | Restricciones                  | Descripción                                  |
| --------------------- | ------------------ | ------------------------------ | -------------------------------------------- |
| `id`                  | `INTEGER IDENTITY` | `PRIMARY KEY`                  | Identificador único generado automáticamente |
| `titulo`              | `VARCHAR(150)`     | `NOT NULL`, `CHECK`            | Título de la solicitud                       |
| `area_solicitante`    | `VARCHAR(100)`     | `NOT NULL`, `CHECK`            | Área que realiza la solicitud                |
| `prioridad`           | `SMALLINT`         | `NOT NULL`, `CHECK`            | Número entre 1 y 5                           |
| `costo_estimado`      | `NUMERIC(12,2)`    | `NOT NULL`, `DEFAULT`, `CHECK` | Costo estimado con dos decimales             |
| `estado`              | `VARCHAR(20)`      | `NOT NULL`, `DEFAULT`, `CHECK` | Estado actual de la solicitud                |
| `fecha_creacion`      | `TIMESTAMPTZ`      | `NOT NULL`, `DEFAULT`          | Fecha de creación                            |
| `fecha_actualizacion` | `TIMESTAMPTZ`      | `NOT NULL`, `DEFAULT`          | Fecha de última modificación                 |


¿Por qué usar estos tipos?
```
INTEGER GENERATED ALWAYS AS IDENTITY
```
Permite que PostgreSQL genere automáticamente el identificador.

Es preferible a utilizar directamente SERIAL, porque IDENTITY pertenece al estándar SQL moderno.
```
VARCHAR
```
Se utiliza para textos que tienen una longitud máxima razonable.

```
titulo VARCHAR(150)
area_solicitante VARCHAR(100)
```

Esto evita almacenar textos excesivamente largos.
```
SMALLINT
```
La prioridad solo acepta valores pequeños entre 1 y 5, por lo que no necesita un INTEGER completo.
```
NUMERIC(12,2)
```
Es recomendable para dinero o costos porque mantiene precisión decimal.

Permite hasta 10 dígitos enteros y 2 decimales, por ejemplo:
```
9999999999.99
```
No se recomienda utilizar FLOAT para cantidades monetarias porque puede generar errores de precisión.
```
TIMESTAMPTZ
```
Registra fecha, hora y zona horaria. Es recomendable cuando la base de datos está alojada en servicios externos como NeonDB.

Restricciones utilizadas
```
PRIMARY KEY
```
Garantiza que cada solicitud tenga un identificador único.
```
CONSTRAINT pk_solicitudes
    PRIMARY KEY (id)
NOT NULL
```
Evita que los campos obligatorios queden vacíos.
```
CHECK
```
Permite validar los valores antes de guardarlos.

Por ejemplo, la prioridad solamente puede estar entre 1 y 5:
```
CHECK (prioridad BETWEEN 1 AND 5)
```
El costo no puede ser negativo:
```
CHECK (costo_estimado >= 0)
```
El estado solamente puede tener valores permitidos:
```
CHECK (
    estado IN (
        'registrada',
        'en_proceso',
        'finalizada',
        'cancelada'
    )
)
```
#### Ajustes aplicados para garantizar seguridad y limpieza

1. Uso de una llave primaria autogenerada
Se definió el campo id como:

```
id INTEGER GENERATED ALWAYS AS IDENTITY
```
Esto permite que PostgreSQL genere automáticamente un identificador único para cada solicitud. De esta forma, la aplicación no debe calcular manualmente los identificadores, evitando duplicados y errores de integridad.

También se utilizó:
```
PRIMARY KEY (id)
```
para garantizar que cada registro pueda identificarse de manera única.

2. Uso de restricciones NOT NULL

Los campos obligatorios fueron definidos con:

NOT NULL

Esto evita que se guarden solicitudes incompletas, por ejemplo, sin título, área solicitante, prioridad o estado.

Esta validación desde la base de datos funciona como una segunda capa de seguridad, aunque la aplicación también realice validaciones previamente.

3. Validación de valores mediante CHECK

Se agregaron restricciones para impedir que se almacenen datos fuera de los rangos permitidos.

Ejemplo para la prioridad:
```
CHECK (prioridad BETWEEN 1 AND 5)
```
Ejemplo para evitar costos negativos:
```
CHECK (costo_estimado >= 0)
```
Ejemplo para limitar los estados permitidos:
```
CHECK (
    estado IN (
        'registrada',
        'en_proceso',
        'finalizada',
        'cancelada'
    )
)
```
Estas restricciones protegen la integridad de la información, incluso si se intenta insertar directamente un dato inválido desde otro programa o desde un cliente SQL.

4. Uso de NUMERIC para valores monetarios

Se utilizó:
```
NUMERIC(12,2)
```
en lugar de FLOAT.

Esto evita errores de precisión decimal que pueden ocurrir con tipos de punto flotante y garantiza que el costo estimado conserve exactamente dos decimales.

5. Límites de longitud en los textos

Se utilizaron tipos como:
```
VARCHAR(150)
VARCHAR(100)
VARCHAR(20)
```
Esto evita almacenar textos excesivamente largos y establece límites coherentes para cada campo.

También facilita la validación tanto en la aplicación como en la base de datos.

6. Valores predeterminados

Se definieron valores por defecto:
```
costo_estimado NUMERIC(12,2) NOT NULL DEFAULT 0.00
estado VARCHAR(20) NOT NULL DEFAULT 'registrada'
```
Esto evita valores nulos y proporciona un estado inicial consistente cuando se registra una solicitud.

7. Fechas gestionadas por PostgreSQL

Se agregaron:
```
fecha_creacion TIMESTAMPTZ
fecha_actualizacion TIMESTAMPTZ
```
Esto permite registrar cuándo se creó y cuándo se modificó cada solicitud.

El uso de TIMESTAMPTZ resulta adecuado para una base de datos alojada externamente porque maneja la fecha, la hora y la zona horaria. Estos ajustes están presentes en el esquema propuesto del primer prompt.

**Justificación**

Estos ajustes garantizan seguridad e integridad porque la base de datos no acepta fácilmente información incompleta o inválida. También mantienen limpio el esquema, ya que cada campo tiene un tipo de dato y una restricción acordes con su propósito.


### Segundo Prompt:

Voy a trabajar con una arquitectura MVC para tener en cuenta el escalamiento en un futuro .Como tal necesito la elaboración de un CRUD que siga las convenciones REST, que sea un código limpio que siga las buenas practicas de desarrollo utilizando nombres descriptivos y evitando la duplicación de código usando el lenguaje de python. El sistema debe estar predispuesto a conectarse una base de datos PostgreSQL alojada de manera presistente en NeonDB. La API debe comunicarse meadiante formato JSON , la estructura utilizada sera la siguiente: { "titulo":"Adquisicion de nuevo servidor", "area_solicitante": "Infraestructura TI", "prioridad": 3, "costo_estimado": 2500.00, "estado": "registrada" }

![alt text](image-1.png)

#### Respuesta Obtenida

Sí, una arquitectura MVC es apta para tu CRUD porque separa las responsabilidades del sistema y evita que toda la lógica quede mezclada en un solo archivo.

Sin embargo, para que sea más escalable, conviene usar una versión organizada de MVC:

Model: representa los datos y la tabla.
View: en una API REST son las respuestas JSON.
Controller: recibe las solicitudes HTTP y devuelve respuestas.
Service: contiene la lógica del negocio.
Repository: se comunica directamente con PostgreSQL.

Esto sería más completo que usar únicamente MVC puro.

Distribución de carpetas recomendada
```
solicitudes-api/
│
├── app/
│   ├── __init__.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── solicitud_model.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── solicitud_schema.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── solicitud_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── solicitud_service.py
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── solicitud_controller.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── solicitud_routes.py
│   │
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── custom_exceptions.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── response.py
│
├── database/
│   └── init.sql
│
├── tests/
│   ├── __init__.py
│   └── test_solicitudes.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
└── README.md
```
Función de cada carpeta
app/config

Contiene la configuración general del proyecto.
```
config/
└── database.py
```

En database.py se configura la conexión con PostgreSQL en NeonDB.

La URL de conexión se obtiene desde el archivo .env.

Ejemplo de variable:
```
DATABASE_URL=postgresql://usuario:password@host/neondb?sslmode=require
```
La contraseña no debe escribirse directamente en el código.

app/models

Contiene los modelos que representan las tablas de la base de datos.
```
models/
└── solicitud_model.py
```
El modelo Solicitud representará la tabla solicitudes.

Sus atributos serían:
```
id
titulo
area_solicitante
prioridad
costo_estimado
estado
```
El modelo define cómo se almacenan los datos, pero no debe manejar peticiones HTTP.

app/schemas

Contiene las estructuras de entrada y salida de datos.
```
schemas/
└── solicitud_schema.py
```
Aquí se validaría que:
```
titulo no esté vacío.
area_solicitante sea obligatorio.
prioridad esté entre 1 y 5.
costo_estimado no sea negativo.
estado tenga un valor permitido.
```
Por ejemplo, se pueden definir esquemas diferentes para:
```
SolicitudCreate
SolicitudUpdate
SolicitudResponse
```

Esto evita utilizar exactamente la misma estructura para crear, actualizar y responder.

app/repositories

Se encarga exclusivamente del acceso a la base de datos.

```
repositories/
└── solicitud_repository.py
```

Aquí se realizan operaciones como:
```
crear una solicitud
obtener todas las solicitudes
buscar una solicitud por id
actualizar una solicitud
eliminar una solicitud
```

El repositorio no debe decidir reglas del negocio. Solo debe consultar o modificar la base de datos.
Teniendo en cuenta lo siguiente :
* Obtener la información de todas las solicitudes operativas.
* Registrar una nueva solicitud operativa.
* Actualizar completamente la información de una solicitud existente.
* Eliminar una solicitud operativa.
* Actualizar exclusivamente el estado de una solicitud operativa, sin modificar el
resto de sus atributos.

#### Ajustes aplicados para garantizar seguridad y limpieza

1. Separación del código por capas

El proyecto se dividió en:
```
models
schemas
repositories
services
controllers
routes
config
exceptions
```

Cada capa tiene una responsabilidad específica:

* models: representa los datos.
* schemas: valida la entrada.
* repositories: accede a PostgreSQL.
* services: contiene los casos de uso.
* controllers: coordina las solicitudes.
* routes: relaciona las URL con los controladores.
* exceptions: representa errores de la aplicación.

Esta separación evita que las consultas SQL, las validaciones y las respuestas HTTP queden mezcladas en un mismo archivo.

2. Credenciales almacenadas en variables de entorno

La URL de conexión se obtiene desde:
```
.env
```
Por ejemplo:
```
DATABASE_URL=postgresql://usuario:password@host/neondb?sslmode=require
```
La contraseña no debe escribirse directamente dentro del código fuente.

Esto mejora la seguridad porque evita exponer las credenciales en los archivos del proyecto.

3. Uso de .gitignore

El archivo .env debe incluirse en .gitignore:
```
.env
```
De esta manera, las credenciales de NeonDB no se suben accidentalmente al repositorio Git.

Debe proporcionarse un archivo:
```
.env.example
```
con la estructura de las variables, pero sin contraseñas reales:
```
DATABASE_URL=
APP_NAME=Solicitudes API
APP_VERSION=1.0.0
DEBUG=False
```
4. Validación separada de la lógica del negocio

Las validaciones se colocaron en:
```
app/schemas/solicitud_schema.py
```
Esto evita repetir validaciones en distintos controladores.

Por ejemplo, las reglas de prioridad, costo y estado se definen una sola vez y pueden reutilizarse tanto en POST como en PUT.

5. Acceso a la base de datos mediante Repository

Las consultas se concentran en:
```
app/repositories/solicitud_repository.py
```
Esto evita escribir SQL directamente en los controladores o servicios.

Como resultado, si en el futuro cambia la forma de acceder a los datos, las modificaciones se realizan principalmente en el repositorio.

6. Uso de nombres descriptivos

Se utilizaron nombres como:

```py
obtener_por_id()
actualizar_estado()
costo_estimado
area_solicitante
SolicitudRepository
SolicitudService
```
Estos nombres permiten comprender la finalidad de cada función o clase sin necesidad de revisar toda su implementación.

7. Eliminación de duplicación

Las funciones comunes, como las validaciones, la construcción de respuestas y el manejo de errores, se separaron en módulos reutilizables.

Esto sigue el principio DRY:

    No repetir la misma lógica en diferentes partes del código.

**Justificación**

La arquitectura propuesta mejora la limpieza porque cada capa tiene una función definida. También mejora la seguridad al separar las credenciales, validar los datos antes de procesarlos y evitar que el acceso a PostgreSQL quede disperso en diferentes archivos. La organización por capas y el uso de .env aparecen como parte de la respuesta del segundo prompts.

### Tercer prompt

Necesito que refactorices el codigo para poder implementar la peticion PATCH a la base de datos , teniendo en cuenta que el codigo debe ser clean code , seguir los principios SOLID y las convecnciones REST 

![alt text](image-2.png)

#### Respuesta Obtenida

Con lo que indicas, tu API debería manejar estas seis operaciones REST:

| Método | Endpoint                 | Operación                              |
| ------ | ------------------------ | -------------------------------------- |
| GET    | /solicitudes             | Obtener todas las solicitudes          |
| GET    | /solicitudes/{id}        | Obtener una solicitud por ID           |
| POST   | /solicitudes             | Registrar una solicitud                |
| PUT    | /solicitudes/{id}        | Actualizar completamente una solicitud |
| PATCH  | /solicitudes/{id}/estado | Actualizar únicamente el estado        |
| DELETE | /solicitudes/{id}        | Eliminar una solicitud                 |


Para agregar correctamente PATCH, debes refactorizar varias capas.

1. Refactorizar el schema

En tu archivo:
```
app/schemas/solicitud_schema.py
```
agrega una función específica para validar únicamente el estado.
```
from decimal import Decimal, InvalidOperation
from typing import Any


ESTADOS_PERMITIDOS = {
    "registrada",
    "en_proceso",
    "finalizada",
    "cancelada",
}

CAMPOS_SOLICITUD = {
    "titulo",
    "area_solicitante",
    "prioridad",
    "costo_estimado",
    "estado",
}


def validar_solicitud(datos: dict[str, Any]) -> dict[str, str]:
    """
    Valida todos los datos necesarios para crear o reemplazar
    completamente una solicitud.
    """
    errores: dict[str, str] = {}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos deben enviarse como un objeto JSON."
        }

    _validar_campos_obligatorios(datos, errores)
    _validar_campos_no_permitidos(
        datos=datos,
        campos_permitidos=CAMPOS_SOLICITUD,
        errores=errores,
    )

    _validar_titulo(datos.get("titulo"), errores)
    _validar_area_solicitante(
        datos.get("area_solicitante"),
        errores,
    )
    _validar_prioridad(datos.get("prioridad"), errores)
    _validar_costo_estimado(
        datos.get("costo_estimado"),
        errores,
    )
    _validar_estado(datos.get("estado"), errores)

    return errores


def validar_actualizacion_estado(
    datos: dict[str, Any],
) -> dict[str, str]:
    """
    Valida una operación PATCH que únicamente permite modificar
    el estado de una solicitud.
    """
    errores: dict[str, str] = {}
    campos_permitidos = {"estado"}

    if not isinstance(datos, dict):
        return {
            "datos": "Los datos deben enviarse como un objeto JSON."
        }

    if "estado" not in datos:
        errores["estado"] = "Este campo es obligatorio."

    _validar_campos_no_permitidos(
        datos=datos,
        campos_permitidos=campos_permitidos,
        errores=errores,
    )

    _validar_estado(datos.get("estado"), errores)

    return errores


def _validar_campos_obligatorios(
    datos: dict[str, Any],
    errores: dict[str, str],
) -> None:
    for campo in CAMPOS_SOLICITUD:
        if campo not in datos:
            errores[campo] = "Este campo es obligatorio."


def _validar_campos_no_permitidos(
    datos: dict[str, Any],
    campos_permitidos: set[str],
    errores: dict[str, str],
) -> None:
    campos_desconocidos = set(datos.keys()) - campos_permitidos

    if campos_desconocidos:
        errores["campos_no_permitidos"] = (
            "Los siguientes campos no están permitidos: "
            + ", ".join(sorted(campos_desconocidos))
            + "."
        )


def _validar_titulo(
    titulo: object,
    errores: dict[str, str],
) -> None:
    if titulo is None:
        return

    if not isinstance(titulo, str):
        errores["titulo"] = "El título debe ser un texto."
        return

    titulo_limpio = titulo.strip()

    if len(titulo_limpio) < 3:
        errores["titulo"] = (
            "El título debe tener al menos 3 caracteres."
        )
        return

    if len(titulo_limpio) > 150:
        errores["titulo"] = (
            "El título no puede superar los 150 caracteres."
        )


def _validar_area_solicitante(
    area_solicitante: object,
    errores: dict[str, str],
) -> None:
    if area_solicitante is None:
        return

    if not isinstance(area_solicitante, str):
        errores["area_solicitante"] = (
            "El área solicitante debe ser un texto."
        )
        return

    area_limpia = area_solicitante.strip()

    if len(area_limpia) < 2:
        errores["area_solicitante"] = (
            "El área solicitante debe tener al menos 2 caracteres."
        )
        return

    if len(area_limpia) > 100:
        errores["area_solicitante"] = (
            "El área solicitante no puede superar los "
            "100 caracteres."
        )


def _validar_prioridad(
    prioridad: object,
    errores: dict[str, str],
) -> None:
    if prioridad is None:
        return

    if isinstance(prioridad, bool) or not isinstance(prioridad, int):
        errores["prioridad"] = (
            "La prioridad debe ser un número entero."
        )
        return

    if not 1 <= prioridad <= 5:
        errores["prioridad"] = (
            "La prioridad debe estar entre 1 y 5."
        )


def _validar_costo_estimado(
    costo_estimado: object,
    errores: dict[str, str],
) -> None:
    if costo_estimado is None:
        return

    if isinstance(costo_estimado, bool):
        errores["costo_estimado"] = (
            "El costo estimado debe ser un número válido."
        )
        return

    try:
        costo_decimal = Decimal(str(costo_estimado))
    except (InvalidOperation, TypeError, ValueError):
        errores["costo_estimado"] = (
            "El costo estimado debe ser un número válido."
        )
        return

    if not costo_decimal.is_finite():
        errores["costo_estimado"] = (
            "El costo estimado debe ser un número finito."
        )
        return

    if costo_decimal < 0:
        errores["costo_estimado"] = (
            "El costo estimado no puede ser negativo."
        )
        return

    if costo_decimal > Decimal("9999999999.99"):
        errores["costo_estimado"] = (
            "El costo estimado supera el valor permitido."
        )
        return

    if abs(costo_decimal.as_tuple().exponent) > 2:
        errores["costo_estimado"] = (
            "El costo estimado puede tener como máximo "
            "2 decimales."
        )


def _validar_estado(
    estado: object,
    errores: dict[str, str],
) -> None:
    if estado is None:
        return

    if not isinstance(estado, str):
        errores["estado"] = "El estado debe ser un texto."
        return

    if estado not in ESTADOS_PERMITIDOS:
        errores["estado"] = (
            "El estado debe ser registrada, en_proceso, "
            "finalizada o cancelada."
        )
```
La función importante para PATCH es:
```
validar_actualizacion_estado()
```
Esta función rechaza cualquier campo diferente de:
```
estado
```
Por ejemplo, este JSON será válido:
```
{
    "estado": "finalizada"
}
```
Pero este será rechazado:
```
{
    "estado": "finalizada",
    "prioridad": 5
}
```
Porque PATCH /estado solamente debe cambiar el estado.

#### Ajustes aplicados para garantizar seguridad y limpieza

1. Creación de una validación específica para PATCH

Se creó la función:
```py
def validar_actualizacion_estado(
    datos: dict[str, Any],
) -> dict[str, str]:
```
Esta función valida únicamente la actualización del estado.

Esto evita reutilizar incorrectamente la validación completa de POST o PUT, ya que una petición PATCH no necesita enviar todos los campos.

2. Restricción de campos permitidos

Para el endpoint:
```
PATCH /solicitudes/{id}/estado
```
solo se permite:

campos_permitidos = {"estado"}

Por lo tanto, esta solicitud es válida:
```json
{
    "estado": "finalizada"
}
```
Pero esta solicitud debe rechazarse:
```json
{
    "estado": "finalizada",
    "prioridad": 5
}
```
Esto evita que el cliente modifique atributos que no corresponden al endpoint.

3. Validación del tipo de contenido recibido

Se verifica que los datos sean un diccionario:
```py
if not isinstance(datos, dict):
    return {
        "datos": "Los datos deben enviarse como un objeto JSON."
    }
```
Esto impide procesar estructuras inválidas, como listas, cadenas o números.

4. Validación de campos obligatorios

Se comprueba que la petición contenga el campo:
```py
if "estado" not in datos:
    errores["estado"] = "Este campo es obligatorio."
```
Esto evita ejecutar una actualización sin recibir el valor que debe modificarse.

5. Lista controlada de estados

Se definió:
```py
ESTADOS_PERMITIDOS = {
    "registrada",
    "en_proceso",
    "finalizada",
    "cancelada",
}
```

La aplicación únicamente acepta valores incluidos en este conjunto.

Esto evita estados escritos de forma inconsistente, como:

```
Finalizado
en proceso
terminada
cancelado
```
6. Validación del costo estimado

El costo se convierte utilizando:
```py
Decimal(str(costo_estimado))
```
Esto conserva mayor precisión que float.

Además, se valida:

* que sea numérico;
* que no sea infinito;
* que no sea negativo;
* que no supere el límite;
* que tenga máximo dos decimales.

7. Reutilización de funciones privadas

En lugar de repetir todas las reglas, se crearon funciones pequeñas:
```py
_validar_titulo()
_validar_area_solicitante()
_validar_prioridad()
_validar_costo_estimado()
_validar_estado()
_validar_campos_no_permitidos()
```

Esto mejora la limpieza del código porque cada función tiene una responsabilidad específica.
También evita duplicar la validación del estado en diferentes operaciones.

8. Separación entre PUT y PATCH

Se definieron dos validaciones distintas:
```py
validar_solicitud()
```
para crear o reemplazar completamente una solicitud, y:
```py
validar_actualizacion_estado()
```
para modificar exclusivamente el estado.

Esto respeta las convenciones REST:

* PUT: reemplazo completo.
* PATCH: modificación parcial.

**Justificación**

La refactorización mejora la seguridad porque controla exactamente qué campos pueden modificarse y rechaza datos inválidos antes de enviarlos al servicio o al repositorio.

También mejora la limpieza al dividir la validación en funciones reutilizables, eliminar duplicación y mantener separadas las reglas de POST, PUT y PATCH. Estas validaciones y la restricción exclusiva del campo estado aparecen en la respuesta del tercer prompt.