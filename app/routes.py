"""HTTP interface for the todo API.

Thin controllers: read the request, delegate to the service, serialize
the answer. All opinions live one layer down, where unit tests are cheap.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from .services import TodoService


def create_todo_blueprint(service: TodoService) -> Blueprint:
    """Build the todo blueprint wired to the given service (dependency injection)."""
    blueprint = Blueprint("todos", __name__)

    @blueprint.get("/health")
    def get_health():
        """Liveness probe. Optimistic by design."""
        return jsonify({"status": "ok"}), 200

    @blueprint.get("/todos")
    def list_todos():
        """List todos, optionally filtered by the ?status= query parameter."""
        status = request.args.get("status")
        todos = service.list_todos(status=status)
        return jsonify([todo.to_dict() for todo in todos]), 200

    @blueprint.post("/todos")
    def create_todo():
        """Create a todo from a JSON body such as {"title": "..."}."""
        payload = request.get_json(silent=True) or {}
        todo = service.create_todo(payload.get("title"))
        return jsonify(todo.to_dict()), 201

    @blueprint.patch("/todos/<int:todo_id>")
    def change_todo_status(todo_id: int):
        """Change a todo's status from a JSON body such as {"status": "..."}."""
        payload = request.get_json(silent=True) or {}
        todo = service.change_status(todo_id, payload.get("status"))
        return jsonify(todo.to_dict()), 200

    @blueprint.delete("/todos/<int:todo_id>")
    def delete_todo(todo_id: int):
        """Delete a todo. Returns 204 and a moment of silence."""
        service.delete_todo(todo_id)
        return "", 204

    @blueprint.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        """Validation failures become structured 400 responses."""
        return jsonify({"error": str(error)}), 400

    @blueprint.errorhandler(TypeError)
    def handle_type_error(error: TypeError):
        """Type confusion (non-string title/status) also becomes a 400."""
        return jsonify({"error": str(error)}), 400

    @blueprint.errorhandler(LookupError)
    def handle_lookup_error(error: LookupError):
        """Missing resources become structured 404 responses."""
        return jsonify({"error": str(error)}), 404

    return blueprint
