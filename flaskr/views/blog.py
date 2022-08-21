from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flask.views import MethodView

from flaskr.views.auth import login_required
from flaskr.db import get_db


class FirstScreen(MethodView):
    def get(self):
        db = get_db()
        transactions = db.execute(
            "SELECT p.id, assetTicker, avaragePaidValue, amount, operation, transactionDate, author_id, username"
            " FROM transactions p JOIN user u ON p.author_id = u.id"
            " ORDER BY transactionDate DESC"
        ).fetchall()
        return render_template("blog/index.html", transactions=transactions)


class CreateTransaction(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template("blog/create.html")

    def post(self):
        assetTicker = request.form["assetTicker"]
        avaragePaidValue = request.form["avaragePaidValue"]
        amount = request.form["amount"]
        transactionDate = request.form["transactionDate"]
        operation = request.form["operation"]

        error = None

        if not assetTicker:
            error = "assetTicker is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO transactions (assetTicker, avaragePaidValue, amount, operation, transactionDate, author_id)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    assetTicker,
                    avaragePaidValue,
                    amount,
                    operation,
                    transactionDate,
                    g.user["id"],
                ),
            )
            db.commit()
            return redirect(url_for("index"))


def get_transactions(id, check_author=True):
    transactions = (
        get_db()
        .execute(
            "SELECT p.id, assetTicker, avaragePaidValue, amount, transactionDate, operation, author_id, username"
            " FROM transactions p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if transactions is None:
        abort(404, f"Transaction id {id} doesn't exist.")

    if check_author and transactions["author_id"] != g.user["id"]:
        abort(403)

    return transactions


class UpdateTransaction(MethodView):
    decorators = [login_required]

    def get(self, id):
        transactions = get_transactions(id)
        return render_template("blog/update.html", transactions=transactions)

    def post(self, id):
        assetTicker = request.form["assetTicker"]
        avaragePaidValue = request.form["avaragePaidValue"]
        amount = request.form["amount"]
        transactionDate = request.form["transactionDate"]
        operation = request.form["operation"]

        error = None

        if not assetTicker:
            error = "assetTicker is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE transactions SET assetTicker = ?, avaragePaidValue = ?, amount = ?, transactionDate = ?, operation = ?"
                " WHERE id = ?",
                (assetTicker, avaragePaidValue, amount, transactionDate, operation, id),
            )
            db.commit()
            return redirect(url_for("index"))


class DeleteTransaction(MethodView):
    decorators = [login_required]

    # NOTE: I guess this is not working
    def post(self, id):
        get_transactions(id)
        db = get_db()
        db.execute("DELETE FROM transactions WHERE id = ?", (id,))
        db.commit()
        return redirect(url_for("index"))


routes = Blueprint("blog", __name__, url_prefix="")
routes.add_url_rule("/", view_func=FirstScreen.as_view("FirstScreen"))
routes.add_url_rule(
    "/<int:id>/delete/", view_func=DeleteTransaction.as_view("DeleteTransaction")
)
routes.add_url_rule(
    "/<int:id>/update", view_func=UpdateTransaction.as_view("UpdateTransaction")
)
routes.add_url_rule("/create", view_func=CreateTransaction.as_view("CreateTransaction"))
