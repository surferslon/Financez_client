"""Sync API, used by the main Financez app."""

import logging
from dataclasses import asdict
from functools import wraps

from flask import Blueprint, abort, current_app, jsonify, request

from app.presentation.security import same

logger = logging.getLogger(__name__)
api = Blueprint("api", __name__, url_prefix="/api")


def token_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not same(request.headers.get("Authorization", ""), f"Bearer {current_app.config['SYNC_TOKEN']}"):
            logger.warning("Sync: rejected %s %s from %s, wrong token", request.method, request.path, request.remote_addr)
            abort(401)
        return view(*args, **kwargs)

    return wrapper


@api.put("/users/<username>")
@token_required
def put_user(username):
    data = request.get_json()
    current_app.extensions["users"].save(username, data["password_hash"], data["accounts"], data["currencies"])
    return "", 204


@api.get("/users/<username>/entries")
@token_required
def list_entries(username):
    entries = current_app.extensions["entries"].pending(username)
    logger.info("Sync: sending %d pending entries of %r", len(entries), username)
    return jsonify([{**asdict(entry), "total": str(entry.total)} for entry in entries])


@api.post("/users/<username>/entries/delete")
@token_required
def delete_entries(username):
    current_app.extensions["entries"].remove(username, request.get_json()["ids"])
    return "", 204
