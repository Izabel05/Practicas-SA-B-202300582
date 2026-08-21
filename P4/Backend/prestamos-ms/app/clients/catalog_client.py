from uuid import UUID

import httpx

from app.models.errors import ExternalServiceError


class HttpCatalogClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def update_copy_status(self, copy_id: UUID, status: str) -> None:
        try:
            response = httpx.patch(
                f"{self._base_url}/api/v1/ejemplares/{copy_id}/estado",
                json={"estado": status},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ExternalServiceError("no fue posible actualizar el ejemplar en Catálogo") from error
