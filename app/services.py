"""Business logic for todos.

The service layer validates input, enforces the rules, and keeps the
controllers too thin to get into trouble.

Error contract: wrong types raise TypeError, wrong values raise ValueError;
both map to HTTP 400 one layer up. Missing ids raise LookupError (HTTP 404).
"""

from __future__ import annotations

from .models import Todo, TodoStatus
from .repository import InMemoryTodoRepository

MAX_TITLE_LENGTH = 100


class TodoService:
    """Implements the todo lifecycle: create, list, change status, delete."""

    def __init__(self, repository: InMemoryTodoRepository) -> None:
        self._repository = repository

    def create_todo(self, title: str) -> Todo:
        """Create a todo that starts life as OPEN, full of potential."""
        self._validate_title(title)
        todo = Todo(id=self._repository.next_id(), title=title)
        return self._repository.add(todo)

    def list_todos(self, status: str | None = None) -> list[Todo]:
        """List todos, optionally filtered by status."""
        if status is None:
            return self._repository.list_all()
        return self._repository.list_all(self._parse_status(status))

    def change_status(self, todo_id: int, status: str) -> Todo:
        """Transition a todo to a new status. No skipped states; no shortcuts."""
        return self._repository.update_status(todo_id, self._parse_status(status))

    def delete_todo(self, todo_id: int) -> None:
        """Delete a todo by id. Raises LookupError if it does not exist."""
        self._repository.delete(todo_id)

    @staticmethod
    def _validate_title(title: str) -> None:
        if not isinstance(title, str):
            raise TypeError("title must be a string")
        if not title.strip():
            raise ValueError("title must be a non-empty string")
        if len(title) > MAX_TITLE_LENGTH:
            raise ValueError(f"title must be at most {MAX_TITLE_LENGTH} characters")

    @staticmethod
    def _parse_status(status: str) -> TodoStatus:
        if not isinstance(status, str):
            raise TypeError("status must be a string")
        try:
            return TodoStatus(status.lower())
        except ValueError as exc:
            allowed = ", ".join(member.value for member in TodoStatus)
            raise ValueError(f"unknown status {status!r}; expected one of: {allowed}") from exc
