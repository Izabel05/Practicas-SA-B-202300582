from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.models.fine import Fine


class FineRepository(Protocol):
    def create_idempotent(self, fine: Fine) -> Fine: ...

    def find_by_id(self, fine_id: UUID) -> Fine: ...

    def find_by_user(self, user_id: UUID) -> list[Fine]: ...

    def mark_paid(self, fine_id: UUID, paid_at: datetime) -> Fine: ...
