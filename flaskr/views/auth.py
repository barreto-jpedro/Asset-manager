import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask.views import MethodView

from flaskr.db import get_db


class RegisterUser(MethodView):
    def get(self):
        return render_template("auth/register.html")

    def post(self):
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.LoginUser"))

        flash(error)


class LoginUser(MethodView):
    def get(self):
        return render_template("auth/login.html")

    def post(self):
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)


class LogoutUser(MethodView):
    def get(self):
        session.clear()
        return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))

        return view(**kwargs)

    return wrapped_view


routes = Blueprint("auth", __name__, url_prefix="/auth")
routes.add_url_rule("/register", view_func=RegisterUser.as_view("RegisterUser"))
routes.add_url_rule("/login", view_func=LoginUser.as_view("LoginUser"))
routes.add_url_rule("/logout", view_func=LogoutUser.as_view("LogoutUser"))


@routes.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )
