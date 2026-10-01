"""Unit tests for TodoService: the layer with all the opinions."""

import pytest

from app.models import TodoStatus
from app.repository import InMemoryTodoRepository
from app.services import MAX_TITLE_LENGTH, TodoService


@pytest.fixture()
def service() -> TodoService:
    """Provide a fresh service backed by an empty, hopeful backlog."""
    return TodoService(InMemoryTodoRepository())


class TestCreateTodo:
    def test_creates_todo_with_open_status(self, service: TodoService) -> None:
        todo = service.create_todo("Write the exercise")

        assert todo.title == "Write the exercise"
        assert todo.status is TodoStatus.OPEN
        assert todo.created_at is not None

    def test_assigns_sequential_ids(self, service: TodoService) -> None:
        first = service.create_todo("first")
        second = service.create_todo("second")

        assert second.id == first.id + 1

    @pytest.mark.parametrize("title", ["", "   ", "\t\n "])
    def test_rejects_blank_titles(self, service: TodoService, title: str) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            service.create_todo(title)

    def test_rejects_non_string_titles(self, service: TodoService) -> None:
        with pytest.raises(TypeError, match="title must be a string"):
            service.create_todo(42)  # type: ignore[arg-type]

    def test_rejects_overlong_titles(self, service: TodoService) -> None:
        with pytest.raises(ValueError, match="at most"):
            service.create_todo("x" * (MAX_TITLE_LENGTH + 1))

    def test_accepts_title_at_the_limit(self, service: TodoService) -> None:
        todo = service.create_todo("x" * MAX_TITLE_LENGTH)

        assert todo.title == "x" * MAX_TITLE_LENGTH


class TestListTodos:
    def test_lists_all_todos(self, service: TodoService) -> None:
        service.create_todo("alpha")
        service.create_todo("beta")

        assert [todo.title for todo in service.list_todos()] == ["alpha", "beta"]

    def test_filters_by_status(self, service: TodoService) -> None:
        first = service.create_todo("alpha")
        second = service.create_todo("beta")
        service.change_status(second.id, "done")

        open_titles = [todo.title for todo in service.list_todos(status="open")]
        done_titles = [todo.title for todo in service.list_todos(status="done")]

        assert open_titles == [first.title]
        assert done_titles == [second.title]

    def test_rejects_unknown_status_filter(self, service: TodoService) -> None:
        with pytest.raises(ValueError, match="unknown status"):
            service.list_todos(status="someday")


class TestChangeStatus:
    def test_changes_status(self, service: TodoService) -> None:
        todo = service.create_todo("alpha")

        updated = service.change_status(todo.id, "in_progress")

        assert updated.status is TodoStatus.IN_PROGRESS

    def test_accepts_uppercase_status_values(self, service: TodoService) -> None:
        todo = service.create_todo("alpha")

        updated = service.change_status(todo.id, "DONE")

        assert updated.status is TodoStatus.DONE

    def test_rejects_unknown_status(self, service: TodoService) -> None:
        todo = service.create_todo("alpha")

        with pytest.raises(ValueError, match="unknown status"):
            service.change_status(todo.id, "paused")

    def test_rejects_non_string_status(self, service: TodoService) -> None:
        todo = service.create_todo("alpha")

        with pytest.raises(TypeError, match="status must be a string"):
            service.change_status(todo.id, None)  # type: ignore[arg-type]

    def test_unknown_id_raises_lookup_error(self, service: TodoService) -> None:
        with pytest.raises(LookupError, match="not found"):
            service.change_status(999, "done")


class TestDeleteTodo:
    def test_deletes_todo(self, service: TodoService) -> None:
        todo = service.create_todo("alpha")

        service.delete_todo(todo.id)

        assert service.list_todos() == []

    def test_unknown_id_raises_lookup_error(self, service: TodoService) -> None:
        with pytest.raises(LookupError, match="not found"):
            service.delete_todo(999)

    def test_deleted_todo_can_no_longer_be_changed(self, service: TodoService) -> None:
        todo = service.create_todo("alpha")
        service.delete_todo(todo.id)

        with pytest.raises(LookupError, match="not found"):
            service.change_status(todo.id, "done")
