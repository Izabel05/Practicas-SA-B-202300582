import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlsplit

from app.routes import SolicitudRoutes


ResponseBody = dict[str, Any]


class UnsupportedMediaTypeError(Exception):
    """
    Indica que el cuerpo de la petición no fue enviado
    utilizando el tipo de contenido application/json.
    """


class ApiRequestHandler(BaseHTTPRequestHandler):
    """
    Traduce peticiones HTTP en llamadas a la capa de rutas.

    Esta clase solamente se encarga del protocolo HTTP:
    método, URL, encabezados, cuerpo JSON y respuesta.
    """

    server_version = "SolicitudesAPI/1.0"

    def __init__(
        self,
        *args: Any,
        routes: SolicitudRoutes,
        **kwargs: Any,
    ) -> None:
        self._routes = routes
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self._procesar_peticion()

    def do_POST(self) -> None:
        self._procesar_peticion(requiere_cuerpo=True)

    def do_PUT(self) -> None:
        self._procesar_peticion(requiere_cuerpo=True)

    def do_PATCH(self) -> None:
        self._procesar_peticion(requiere_cuerpo=True)

    def do_DELETE(self) -> None:
        self._procesar_peticion()

    def do_OPTIONS(self) -> None:
        """
        Informa los métodos HTTP generales admitidos por la API.
        """
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header(
            "Allow",
            "GET, POST, PUT, PATCH, DELETE, OPTIONS",
        )
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _procesar_peticion(
        self,
        requiere_cuerpo: bool = False,
    ) -> None:
        """
        Procesa la petición HTTP y la envía al componente de rutas.
        """
        try:
            datos = (
                self._leer_cuerpo_json()
                if requiere_cuerpo
                else None
            )

            cuerpo, codigo_estado = self._routes.procesar(
                metodo=self.command,
                ruta=self._obtener_ruta(),
                datos=datos,
            )

            self._enviar_respuesta(
                cuerpo=cuerpo,
                codigo_estado=codigo_estado,
            )

        except UnsupportedMediaTypeError as error:
            self._enviar_error_http(
                codigo_estado=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                codigo_error="UNSUPPORTED_MEDIA_TYPE",
                mensaje=str(error),
            )

        except json.JSONDecodeError:
            self._enviar_error_http(
                codigo_estado=HTTPStatus.BAD_REQUEST,
                codigo_error="INVALID_JSON",
                mensaje=(
                    "El cuerpo de la petición contiene un JSON "
                    "inválido."
                ),
            )

        except ValueError as error:
            self._enviar_error_http(
                codigo_estado=HTTPStatus.BAD_REQUEST,
                codigo_error="INVALID_REQUEST_BODY",
                mensaje=str(error),
            )

        except Exception:
            self._enviar_error_http(
                codigo_estado=(
                    HTTPStatus.INTERNAL_SERVER_ERROR
                ),
                codigo_error="INTERNAL_SERVER_ERROR",
                mensaje=(
                    "Ocurrió un error interno al procesar "
                    "la petición."
                ),
            )

    def _leer_cuerpo_json(self) -> dict[str, Any]:
        """
        Lee y convierte el cuerpo de la petición a un diccionario.

        Lanza una excepción cuando el contenido no es JSON válido.
        """
        self._validar_tipo_contenido()

        longitud = self._obtener_longitud_contenido()

        if longitud == 0:
            return {}

        contenido = self.rfile.read(longitud)
        texto = contenido.decode("utf-8")

        datos = json.loads(texto)

        if not isinstance(datos, dict):
            raise ValueError(
                "El cuerpo JSON debe ser un objeto."
            )

        return datos

    def _validar_tipo_contenido(self) -> None:
        """
        Comprueba que la petición declare application/json.
        """
        tipo_contenido = self.headers.get(
            "Content-Type",
            "",
        )

        tipo_principal = tipo_contenido.split(
            ";",
            maxsplit=1,
        )[0].strip().lower()

        if tipo_principal != "application/json":
            raise UnsupportedMediaTypeError(
                "El encabezado Content-Type debe ser "
                "application/json."
            )

    def _obtener_longitud_contenido(self) -> int:
        """
        Obtiene la cantidad de bytes enviados en el cuerpo.
        """
        valor = self.headers.get("Content-Length")

        if valor is None:
            return 0

        try:
            longitud = int(valor)
        except ValueError as error:
            raise ValueError(
                "El encabezado Content-Length no es válido."
            ) from error

        if longitud < 0:
            raise ValueError(
                "El encabezado Content-Length no puede ser negativo."
            )

        return longitud

    def _obtener_ruta(self) -> str:
        """
        Obtiene únicamente la ruta, sin parámetros de consulta.
        """
        return urlsplit(self.path).path

    def _enviar_respuesta(
        self,
        cuerpo: ResponseBody,
        codigo_estado: int,
    ) -> None:
        """
        Envía la respuesta HTTP en formato JSON.

        Las respuestas 204 no deben contener cuerpo.
        """
        self.send_response(codigo_estado)

        self._agregar_encabezado_allow(
            cuerpo=cuerpo,
            codigo_estado=codigo_estado,
        )

        if codigo_estado == HTTPStatus.NO_CONTENT:
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        contenido = json.dumps(
            cuerpo,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(contenido)),
        )
        self.end_headers()
        self.wfile.write(contenido)

    def _enviar_error_http(
        self,
        codigo_estado: int,
        codigo_error: str,
        mensaje: str,
    ) -> None:
        """
        Genera una respuesta uniforme para errores HTTP.
        """
        cuerpo = {
            "error": {
                "code": codigo_error,
                "message": mensaje,
            }
        }

        self._enviar_respuesta(
            cuerpo=cuerpo,
            codigo_estado=codigo_estado,
        )

    def _agregar_encabezado_allow(
        self,
        cuerpo: ResponseBody,
        codigo_estado: int,
    ) -> None:
        """
        Agrega el encabezado Allow en respuestas HTTP 405.
        """
        if codigo_estado != HTTPStatus.METHOD_NOT_ALLOWED:
            return

        metodos = (
            cuerpo
            .get("error", {})
            .get("details", {})
            .get("allowed_methods")
        )

        if metodos:
            self.send_header("Allow", str(metodos))

    def log_message(
        self,
        format: str,
        *args: Any,
    ) -> None:
        """
        Personaliza el registro de peticiones del servidor.
        """
        mensaje = format % args

        print(
            f"{self.client_address[0]} "
            f"- {self.command} {self.path} "
            f"- {mensaje}"
        )