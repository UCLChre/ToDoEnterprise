"""ToDoEnterprise application package.

An application factory, because global state is how todo lists die.
"""

from __future__ import annotations

from flask import Flask

from .repository import InMemoryTodoRepository
from .routes import create_todo_blueprint
from .services import TodoService


def create_app() -> Flask:
    """Create the Flask app and wire the object graph by hand.

    Three classes do not need a dependency-injection framework; they need
    five lines of honest constructor calls.
    """
    app = Flask(__name__)
    repository = InMemoryTodoRepository()
    service = TodoService(repository)
    app.register_blueprint(create_todo_blueprint(service))
    return app
