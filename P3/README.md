# Práctica 3 — Diseño de un sistema bancario de procesamiento de lotes

## 1. Descripción de la solución

La propuesta sustituye el procesamiento monolítico por una arquitectura de microservicios orientada al procesamiento de transacciones bancarias por lotes. Su objetivo es separar responsabilidades que tienen diferentes cargas, ritmos de cambio y riesgos: autenticación, recepción y validación de archivos CSV, aprobación, envío al core bancario y notificación a beneficiarios.

La separación permite que, durante periodos de alta demanda —fin de mes, pago de planillas, temporadas de impuestos o cargas masivas—, los servicios con mayor actividad puedan escalar sin tener que replicar todo el sistema. También limita el impacto de una falla: una indisponibilidad temporal del proveedor de correo no debe alterar la información del lote ni las decisiones de aprobación.

| Microservicio | Responsabilidad | Motivo de la separación |
|---|---|---|
| Autenticación y autorización | Validar identidad, token corporativo y permisos | La seguridad es transversal y no debe duplicarse |
| Lotes y transacciones | Recibir el CSV, validarlo, almacenar su referencia y conservar las transacciones | Es el propietario del lote y sus reglas de carga |
| Aprobaciones | Administrar Maker–Checker–Authorizer y su historial | La segregación de funciones exige reglas y auditoría propias |
| Procesamiento | Enviar lotes aprobados al core y registrar resultados e intentos | Aísla la integración bancaria y sus fallos |
| Notificaciones | Enviar correos y controlar intentos y resultados | El correo tiene disponibilidad y tiempos distintos al procesamiento |

Cada microservicio es dueño de sus datos. Ninguno consulta directamente la base de datos de otro. Los identificadores externos almacenados en una tabla, como `id_lote`, `id_transaccion` o `id_usuario`, son referencias lógicas y no llaves foráneas entre bases de datos.

## 2. Diagrama de arquitectura general

![Diagrama de arquitectura](Imagenes/Diagrama%20-%20Arquitectura.png)

### Justificación

La aplicación web es el punto de interacción del **empleado bancario**, porque Maker, Checker y Authorizer son funciones internas desempeñadas por distintos empleados. Los clientes o beneficiarios reciben notificaciones, pero no ejecutan el flujo de aprobación.

El API Gateway es la entrada controlada. Recibe solicitudes, aplica políticas generales y dirige cada petición al microservicio responsable. En esta propuesta también media las llamadas REST entre microservicios. Esto oculta direcciones internas y centraliza autenticación, enrutamiento, límites y trazabilidad.

Cada servicio posee una base independiente (*Database per Service*). Así se evita el acoplamiento mediante tablas compartidas y cada servicio puede evolucionar sin modificar el esquema de otro.

El repositorio CSV se separa de la base porque los archivos son objetos de tamaño variable. La base de Lotes conserva metadatos —nombre, ubicación, hash, tamaño, estado y fecha— y el contenido se guarda en almacenamiento de objetos o SFTP.

El core bancario, el proveedor OAuth y el servicio de correo están fuera del límite porque son dependencias externas que el sistema consume, pero no administra.

### Significado de las líneas

| Representación | Significado |
|---|---|
| Línea continua con flecha | Comunicación síncrona o dependencia dirigida; el origen inicia la solicitud |
| Línea discontinua hacia Logging | Envío de logs estructurados; no representa una operación del negocio |
| `HTTPS/REST` | API síncrona protegida con TLS y mensajes JSON |
| `Bearer Token` | Credencial enviada en el encabezado de autorización |
| `SQL` | Acceso privado del servicio a su propia base |
| `SMTP/API` | Integración con el proveedor externo de correo |

Una conexión REST ya implica solicitud y respuesta, por lo que no requiere dos flechas paralelas. Se usa HTTPS, no HTTP, para proteger tokens, información bancaria y datos personales durante el transporte.

### Decisión de no utilizar bus de eventos

La propuesta utiliza HTTPS/REST por medio del API Gateway. No incluye bus de eventos porque el alcance se resolvió con flujos claros que requieren una respuesta: validar, aprobar, enviar al core y solicitar notificaciones.

REST simplifica el diseño inicial, la trazabilidad y el manejo de errores, aunque crea dependencia temporal. Se mitiga con *timeouts*, reintentos controlados, idempotencia, *circuit breaker* y correlación de solicitudes. Una cola podría incorporarse en una evolución futura si el volumen exigiera procesamiento asíncrono.

## 3. Integración de autenticación

El sistema combina dos responsabilidades:

1. El proveedor OAuth corporativo autentica la identidad y emite un token con vida de 12 horas.
2. El servicio de autenticación y autorización administra usuarios, roles y permisos, siguiendo el propósito del módulo de la Práctica 2. Esto representa reutilización conceptual de autenticación, permisos y accesos; no obliga a reutilizar su código, tecnología ni estructura interna.

Flujo propuesto:

1. El empleado se autentica contra el proveedor OAuth.
2. La aplicación presenta el token como `Bearer Token` al Gateway.
3. El Gateway solicita al servicio de autenticación validar token, vigencia y acceso.
4. El servicio relaciona la identidad corporativa (`oauth_subject`) con el usuario local y consulta roles y permisos.
5. Solo después de autorizar, el Gateway enruta la solicitud.

Los permisos distinguen acciones como crear, revisar y autorizar lotes. Además del rol, Aprobaciones valida que Maker, Checker y Authorizer sean usuarios distintos; esta regla no depende únicamente del token.

## 4. Diagrama de componentes UML

![Diagrama de componentes](Imagenes/Diagrama%20-%20Componentes.png)

### Justificación

Este diagrama muestra unidades desplegables y dependencias, no el orden temporal. Incluye aplicación web, Gateway, cinco microservicios, bases independientes, repositorio CSV, logging y sistemas externos.

Las líneas continuas representan interfaces utilizadas. Los conectores tipo círculo pueden destacar una interfaz provista o requerida, pero no es necesario colocarlos en cada unión si las etiquetas son legibles. Lo importante es conservar una notación coherente y una leyenda.

Las bases aparecen para evidenciar persistencia independiente. Debe existir únicamente una conexión entre cada servicio y su propia base. El Gateway se conecta a los cinco servicios; Procesamiento al core, Notificaciones al correo, Autenticación al OAuth y Lotes al repositorio CSV. Todos envían logs estructurados al logging centralizado.

## 5. Diagramas entidad–relación

Los ER se separan por microservicio para mantener propiedad independiente de los datos. Las relaciones dibujadas son locales; los IDs de otros servicios son referencias lógicas verificadas mediante API.

### 5.1 Autenticación y autorización

![ER de autenticación](Imagenes/Diagrama%20-%20ER_de_Autenticacion.png)

`Usuario` vincula identidad corporativa y cuenta local. `Rol` agrupa responsabilidades y `Permiso` acciones autorizables. `UsuarioRol` y `RolPermiso` resuelven relaciones muchos a muchos. Los UUID evitan depender de secuencias globales.

### 5.2 Lotes y transacciones

![ER de lotes y transacciones](Imagenes/Diagrama%20-%20ER-LotesYTransacciones.png)

`Lote` conserva resumen, estado y totales; `ArchivoCSV`, ubicación e integridad; `Transaccion`, cada fila; y `ErrorValidacion`, las reglas incumplidas. Un lote contiene muchas transacciones y una transacción puede tener cero o varios errores. Aquí se registran validaciones de saldo, límites, cuentas válidas y prevención de fraude.

### 5.3 Aprobaciones

![ER de aprobaciones](Imagenes/Diagrama%20-%20ER-ServicioAprobaciones.png)

`ProcesoAprobacion` representa la aprobación; `PasoAprobacion`, cada etapa; e `HistorialAprobaciones`, la evidencia auditable. La regla “exactamente tres pasos” se implementa con `numero_paso` 1, 2 y 3 y una restricción única por proceso. `id_lote` e `id_usuario` son referencias externas.

### 5.4 Procesamiento

![ER de procesamiento](Imagenes/Diagrama%20-%20ER-ServicioProcesamiento.png)

`ProcesamientoLote` resume la ejecución; `IntentoEnvio` controla reintentos, correlación y errores; y `ResultadoTransaccion` conserva la respuesta individual del core. Esto mantiene trazabilidad cuando parte del lote falla. `id_lote` e `id_transaccion` son referencias lógicas.

### 5.5 Notificaciones

![ER de notificaciones](Imagenes/Diagrama%20-%20ER-ServicioNotificaciones.png)

El modelo distingue el proceso del lote, la notificación de cada beneficiario y sus intentos. Permite estados `COMPLETADA`, `PARCIAL` o `FALLIDA`, limitar reintentos y conservar la respuesta del proveedor.

## 6. Diagramas de clases UML

Los diagramas describen el dominio de cada microservicio: entidades, atributos, comportamientos y relaciones. No es obligatorio agregar controladores o repositorios porque el alcance solicita entidades principales.

### 6.1 Autenticación

![Clases de autenticación](Imagenes/Diagrama%20-%20UML-Autenticacion.png)

`Usuario`, `Rol`, `Permiso`, `UsuarioRol` y `RolPermiso` modelan identidad y autorización. Las operaciones expresan comportamientos como verificar estado o comprobar permisos.

### 6.2 Lotes y transacciones

![Clases de lotes y transacciones](Imagenes/Diagrama%20-%20UML-ServicioLotesyTransacciones.png)

`Lote` es la entidad principal y agrupa archivo y transacciones. Las operaciones de validar, calcular totales y cambiar estado pertenecen al dominio. `ErrorValidacion` explica por qué una transacción no continúa.

### 6.3 Aprobaciones

![Clases de aprobaciones](Imagenes/Diagrama%20-%20UML-Aprobaciones.png)

`ProcesoAprobacion` controla paso actual y estado. `PasoAprobacion` registra rol, usuario y decisión. `HistorialAprobacion` conserva transiciones. Sus operaciones impiden saltar pasos o repetir un usuario.

### 6.4 Procesamiento

![Clases de procesamiento](Imagenes/Diagrama%20-%20UML-Procesamiento.png)

`ProcesamientoLote` administra el ciclo de envío; `IntentoEnvio`, cada comunicación con el core; y `ResultadoTransaccion`, la respuesta individual.

### 6.5 Notificaciones

![Clases de notificaciones](Imagenes/Diagrama%20-%20UML-Notificaciones.png)

Las clases separan el resumen del lote, el envío por beneficiario y cada intento. Así se reintenta un correo sin repetir los exitosos y se calcula un estado final verificable.

## 7. Diagramas de secuencia UML

### 7.1 Aprobación de tres pasos

![Secuencia de aprobación](Imagenes/Diagrama%20-%20UML-Secuencia1.png)

Maker, Checker y Authorizer son actores porque representan empleados. El flujo es:

1. **Maker:** selecciona un lote validado, solicita aprobación, se verifica su permiso, se crea el proceso con tres pasos, se completa el primero y se habilita el segundo.
2. **Checker:** revisa y decide. Se valida su permiso y que no sea el Maker. Si aprueba, completa el segundo paso y habilita el tercero.
3. **Authorizer:** autoriza finalmente. Debe ser distinto de los dos anteriores. Si aprueba, completa el paso 3, el proceso queda `APROBADO` y se actualiza el lote.

Los fragmentos `alt` representan operación válida o rechazo por rol, paso incorrecto o usuario repetido. Cada decisión guarda usuario, fecha, estado anterior, estado nuevo y comentario.

### 7.2 Envío al core bancario

![Secuencia de envío al core](Imagenes/Diagrama%20-%20UML-Secuencia2.png)

Procesamiento consulta el lote mediante el Gateway y solo continúa si está aprobado. Crea el procesamiento, obtiene transacciones, registra el intento y envía al core. La respuesta se almacena por transacción. El `alt` diferencia respuesta de error o *timeout*. Los reintentos son limitados e idempotentes para evitar duplicar transferencias.

### 7.3 Notificación a beneficiarios

![Secuencia de notificaciones](Imagenes/Diagrama%20-%20UML-Secuencia3.png)

Después del paso 3, Aprobaciones solicita la notificación por el Gateway. Notificaciones obtiene beneficiarios desde Lotes, verifica el estado aprobado y crea el proceso. Un `loop` envía a cada beneficiario el mensaje de que su transacción está en proceso. El `alt` registra éxito o error; se proponen tres intentos. El cliente no es actor porque no inicia la interacción: recibe el correo.

## 8. Estrategia de almacenamiento CSV

Se propone almacenamiento de objetos en nube para producción o SFTP en un ambiente controlado, abstraído por el servicio de Lotes.

1. Recibir el archivo con autenticación, límite de tamaño y extensión permitida.
2. Generar `id_lote` y un nombre interno no predecible.
3. Validar formato, encabezados, columnas y tipos.
4. Calcular SHA-256 para integridad y detección de duplicados.
5. Guardar en `lotes/{año}/{mes}/{id_lote}/original.csv`.
6. Registrar ubicación, nombre original, hash, tamaño, estado y fecha.
7. Procesar filas y persistir transacciones y errores.
8. Autorizar la descarga y entregar un enlace temporal, sin exponer el repositorio.

El almacenamiento debe cifrarse en reposo, usar TLS, ser privado y contar con retención, respaldo y versionado.

## 9. Logging centralizado y auditable

Todos los servicios generan logs JSON para una plataforma centralizada de búsqueda y retención, como OpenSearch/ELK o equivalente.

Cada registro incluye fecha UTC, nivel, servicio, ambiente, `correlation_id`, `request_id`, identificadores pertinentes, acción, resultado, duración y código de respuesta. No se registran tokens, contraseñas, cuentas completas ni contenido sensible del CSV; deben enmascararse.

Además del logging técnico, las decisiones de aprobación y operaciones financieras forman una auditoría con actor, acción, fecha y transición de estado. Los registros deben protegerse contra alteración, tener acceso restringido y retención según políticas bancarias.

## 10. Comunicación entre servicios

La comunicación es HTTPS/REST con JSON:

- aplicación → Gateway: solicitudes con Bearer Token;
- Gateway → Autenticación: identidad y permisos;
- Gateway → Lotes: carga, validación, historial y descarga;
- Gateway → Aprobaciones: decisiones de los tres pasos;
- Aprobaciones → Gateway → Procesamiento: envío de lote aprobado;
- Aprobaciones → Gateway → Notificaciones: correos tras el paso 3;
- Procesamiento/Notificaciones → Gateway → Lotes: consulta de transacciones o beneficiarios;
- Procesamiento → Core: transacciones y resultados;
- Notificaciones → correo: SMTP seguro o API HTTPS.

Se propagan `correlation_id` e idempotencia y se configuran *timeouts*, reintentos para fallos transitorios y *circuit breaker*.

## 11. Propuesta de API Gateway

Se propone **Kong Gateway** o una solución equivalente como punto único de entrada. Debe ofrecer:

- terminación TLS y exposición HTTPS;
- validación o delegación de tokens OAuth;
- rutas versionadas, por ejemplo `/api/v1/lotes`;
- propagación segura de identidad;
- *rate limiting* para alta demanda;
- generación de `correlation_id`;
- límites de tamaño y tiempo;
- logs de acceso y métricas;
- CORS para la aplicación web;
- ocultamiento de direcciones internas.

El Gateway no contiene reglas bancarias, no consulta bases de negocio y no reemplaza los microservicios. Su función es proteger, gobernar y enrutar la comunicación.
