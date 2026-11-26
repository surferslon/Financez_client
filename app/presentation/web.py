"""Web interface."""

import hashlib
import secrets
import time
from datetime import date
from functools import wraps

from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, session, url_for

from app.domain.entry import InvalidEntry
from app.presentation.security import same

web = Blueprint("web", __name__)


def fingerprint(user):
    return hashlib.sha256(user.password_hash.encode()).hexdigest()


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_app.extensions["users"].get(session.get("username", ""))
        # A password change in Financez ends the session
        if not user or session.get("fingerprint") != fingerprint(user):
            session.clear()
            return redirect(url_for("web.login"))
        g.user = user
        if request.method == "POST" and not same(request.form.get("csrf", ""), session["csrf"]):
            abort(400)
        return view(*args, **kwargs)

    return wrapper


@web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = current_app.extensions["users"].authenticate(request.form.get("username", ""), request.form.get("password", ""))
        if user:
            session.clear()
            session.permanent = True
            session["username"] = user.username
            session["fingerprint"] = fingerprint(user)
            session["csrf"] = secrets.token_urlsafe()
            return redirect(url_for("web.index"))
        time.sleep(current_app.config["LOGIN_DELAY"])
        flash("Wrong username or password")
    return render_template("login.html")


@web.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("web.login"))


@web.get("/")
@login_required
def index():
    pending = current_app.extensions["entries"].pending(g.user.username)
    return render_template(
        "index.html",
        user=g.user,
        tree=g.user.account_tree(),
        currencies=g.user.currencies,
        entries=pending[::-1],
        account_names={account["id"]: account["name"] for account in g.user.accounts},
        currency_names={currency["id"]: currency["name"] for currency in g.user.currencies},
        today=date.today().isoformat(),
        last=session.get("last", {}),
    )


@web.post("/entries")
@login_required
def create_entry():
    fields = ("date", "acc_dr", "acc_cr", "currency", "total", "comment")
    try:
        entry = current_app.extensions["entries"].add(g.user, *(request.form.get(field, "") for field in fields))
    except InvalidEntry:
        flash("Invalid entry")
    else:
        session["last"] = {"acc_dr": entry.acc_dr, "acc_cr": entry.acc_cr, "currency": entry.currency}
        flash("Saved")
    return redirect(url_for("web.index"))


@web.post("/entries/<entry_id>/delete")
@login_required
def delete_entry(entry_id):
    current_app.extensions["entries"].remove(g.user.username, [entry_id])
    return redirect(url_for("web.index"))
