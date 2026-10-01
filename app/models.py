"""Domain models: the sacred data structures of the todo empire."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone


class TodoStatus(str, enum.Enum):
    """The three states of a todo's life. There is no CANCELLED. We do not cancel."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass(slots=True)
class Todo:
    """A single todo item, plus metadata worthy of an audit trail."""

    id: int
    title: str
    status: TodoStatus = TodoStatus.OPEN
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, object]:
        """Serialize to a JSON-friendly dictionary for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }
