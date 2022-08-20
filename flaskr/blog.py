from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flask.views import MethodView

from flaskr.auth import login_required
from flaskr.db import get_db


class FirstScreen(MethodView):
    def get(self):
        db = get_db()
        posts = db.execute(
            'SELECT p.id, title, body, amount, operation, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()
        return render_template('blog/index.html', posts=posts)


class CreatePost(MethodView):
    decorators = [login_required]
    
    def get(self):
        return render_template('blog/create.html')

    def post(self):
        ticker = request.form['ticker']
        price = request.form['price']
        amount = request.form['amount']
        created = request.form['created']
        operation = request.form['operation']
        
        error = None

        if not ticker:
            error = 'Ticker is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, amount, operation, created, author_id)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (ticker, price, amount, operation, created, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, amount, created, operation, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


class UpdatePost(MethodView):
    decorators = [login_required]

    def get(self, id):
        post = get_post(id)
        return render_template('blog/update.html', post=post)

    
    def post(self, id):
        ticker = request.form['ticker']
        price = request.form['price']
        amount = request.form['amount']
        created = request.form['created']
        operation = request.form['operation']

        error = None

        if not ticker:
            error = 'Ticker is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, amount = ?, created = ?, operation = ?'
                ' WHERE id = ?',
                (ticker, price, amount, created, operation, id)
            )
            db.commit()
            return redirect(url_for('index'))


class DeletePost(MethodView):
    decorators = [login_required]

    def post(self, id):
        get_post(id)
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('index'))


routes = Blueprint('blog', __name__, url_prefix='')
routes.add_url_rule('/', view_func=FirstScreen.as_view("FirstScreen"))
routes.add_url_rule('/<int:id>/delete/', view_func=DeletePost.as_view("DeletePost"))
routes.add_url_rule('/<int:id>/update', view_func=UpdatePost.as_view("UpdatePost"))
routes.add_url_rule('/create', view_func=CreatePost.as_view("CreatePost"))
