"""Financez client: collects entries until the main Financez app picks them up.

Layers, each one only using the ones below it:
    presentation  HTTP: web interface and sync API
    services      use cases
    repositories  SQLite storage
    domain        entry model and its rules (used by all layers above)

This module wires them together.
"""

import logging

from flask import Flask

from app.config import load_config
from app.presentation.api import api
from app.presentation.web import web
from app.repositories.database import Database
from app.repositories.entries import EntryRepository
from app.repositories.users import UserRepository
from app.services.entries import EntryService
from app.services.users import UserService


def setup_logging():
    logger = logging.getLogger("app")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def create_app(overrides=None):
    setup_logging()
    app = Flask(__name__, template_folder="presentation/templates", static_folder="presentation/static")
    app.config.update(load_config(overrides))

    database = Database(app.config["DATABASE"])
    app.extensions["users"] = UserService(UserRepository(database))
    app.extensions["entries"] = EntryService(EntryRepository(database))

    app.register_blueprint(web)
    app.register_blueprint(api)
    return app
