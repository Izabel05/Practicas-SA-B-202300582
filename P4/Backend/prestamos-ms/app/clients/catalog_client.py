from uuid import UUID

import httpx
from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.trace import SpanKind

from app.models.errors import ExternalServiceError


class HttpCatalogClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def update_copy_status(self, copy_id: UUID, status: str) -> None:
        headers: dict[str, str] = {}
        inject(headers)
        try:
            with trace.get_tracer(__name__).start_as_current_span(
                "catalogo.actualizar_estado", kind=SpanKind.CLIENT
            ) as span:
                span.set_attribute("library.copy.id", str(copy_id))
                span.set_attribute("library.copy.status", status)
                response = httpx.patch(
                    f"{self._base_url}/api/v1/ejemplares/{copy_id}/estado",
                    json={"estado": status},
                    headers=headers,
                    timeout=self._timeout,
                )
                span.set_attribute("http.response.status_code", response.status_code)
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise ExternalServiceError("no fue posible actualizar el ejemplar en Catálogo") from error
