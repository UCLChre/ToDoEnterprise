"""Route tests for the todo API, driven through Flask's test client."""

import pytest

from app import create_app


@pytest.fixture()
def client():
    """Provide a test client backed by a fresh, empty application."""
    application = create_app()
    application.testing = True
    return application.test_client()


class TestHealth:
    def test_returns_ok(self, client) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestCreateTodo:
    def test_creates_todo(self, client) -> None:
        response = client.post("/todos", json={"title": "Ship the exercise"})

        assert response.status_code == 201
        body = response.get_json()
        assert body["title"] == "Ship the exercise"
        assert body["status"] == "open"
        assert isinstance(body["id"], int)
        assert "created_at" in body

    @pytest.mark.parametrize("payload", [{}, {"title": ""}, {"title": "   "}])
    def test_rejects_missing_or_blank_title(self, client, payload) -> None:
        response = client.post("/todos", json=payload)

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_rejects_non_string_title(self, client) -> None:
        response = client.post("/todos", json={"title": 42})

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_rejects_overlong_title(self, client) -> None:
        response = client.post("/todos", json={"title": "x" * 101})

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_rejects_malformed_json_body(self, client) -> None:
        response = client.post("/todos", data="{not json", content_type="application/json")

        assert response.status_code == 400
        assert "error" in response.get_json()


class TestListTodos:
    def test_lists_created_todos(self, client) -> None:
        created = client.post("/todos", json={"title": "alpha"}).get_json()

        response = client.get("/todos")

        assert response.status_code == 200
        assert response.get_json() == [created]

    def test_filters_by_status(self, client) -> None:
        client.post("/todos", json={"title": "alpha"})
        second = client.post("/todos", json={"title": "beta"}).get_json()
        client.patch(f"/todos/{second['id']}", json={"status": "done"})

        open_titles = [todo["title"] for todo in client.get("/todos?status=open").get_json()]
        done_titles = [todo["title"] for todo in client.get("/todos?status=done").get_json()]

        assert open_titles == ["alpha"]
        assert done_titles == ["beta"]

    def test_rejects_unknown_status_filter(self, client) -> None:
        response = client.get("/todos?status=someday")

        assert response.status_code == 400
        assert "error" in response.get_json()


class TestChangeStatus:
    def test_changes_status(self, client) -> None:
        todo_id = client.post("/todos", json={"title": "alpha"}).get_json()["id"]

        response = client.patch(f"/todos/{todo_id}", json={"status": "in_progress"})

        assert response.status_code == 200
        assert response.get_json()["status"] == "in_progress"

    def test_rejects_unknown_status(self, client) -> None:
        todo_id = client.post("/todos", json={"title": "alpha"}).get_json()["id"]

        response = client.patch(f"/todos/{todo_id}", json={"status": "paused"})

        assert response.status_code == 400
        assert "error" in response.get_json()

    @pytest.mark.parametrize("payload", [{}, {"status": ["done"]}])
    def test_rejects_missing_or_non_string_status(self, client, payload) -> None:
        todo_id = client.post("/todos", json={"title": "alpha"}).get_json()["id"]

        response = client.patch(f"/todos/{todo_id}", json=payload)

        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_returns_404_for_unknown_id(self, client) -> None:
        response = client.patch("/todos/999", json={"status": "done"})

        assert response.status_code == 404
        assert response.get_json() == {"error": "todo 999 not found"}

    def test_returns_404_for_non_numeric_id(self, client) -> None:
        response = client.patch("/todos/soon", json={"status": "done"})

        assert response.status_code == 404


class TestDeleteTodo:
    def test_deletes_todo(self, client) -> None:
        todo_id = client.post("/todos", json={"title": "alpha"}).get_json()["id"]

        response = client.delete(f"/todos/{todo_id}")

        assert response.status_code == 204
        assert response.data == b""
        assert client.get("/todos").get_json() == []

    def test_returns_404_for_unknown_id(self, client) -> None:
        response = client.delete("/todos/999")

        assert response.status_code == 404
        assert response.get_json() == {"error": "todo 999 not found"}
