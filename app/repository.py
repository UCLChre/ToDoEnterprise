"""In-memory persistence for todos.

Horizontally scalable to exactly one process. Swap this class for a real
database repository once the board approves the database line item.
"""

from __future__ import annotations

from .models import Todo, TodoStatus


class InMemoryTodoRepository:
    """Stores todos in a dictionary and guards them like a dragon guards gold."""

    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._next_id = 1

    def next_id(self) -> int:
        """Reserve the next sequential id. Counting: the original key-value store."""
        next_id = self._next_id
        self._next_id += 1
        return next_id

    def add(self, todo: Todo) -> Todo:
        """Store a todo and return it (the same one; this is not a trick)."""
        self._todos[todo.id] = todo
        return todo

    def get(self, todo_id: int) -> Todo:
        """Return the todo with the given id."""
        try:
            return self._todos[todo_id]
        except KeyError as exc:
            raise LookupError(f"todo {todo_id} not found") from exc

    def list_all(self, status: TodoStatus | None = None) -> list[Todo]:
        """Return all todos, optionally filtered by status."""
        if status is None:
            return list(self._todos.values())
        return [todo for todo in self._todos.values() if todo.status == status]

    def update_status(self, todo_id: int, status: TodoStatus) -> Todo:
        """Set a new status on the stored todo and return it."""
        todo = self.get(todo_id)
        todo.status = status
        return todo

    def delete(self, todo_id: int) -> None:
        """Remove the todo with the given id."""
        try:
            del self._todos[todo_id]
        except KeyError as exc:
            raise LookupError(f"todo {todo_id} not found") from exc
