import click
from functools import wraps
from flask import abort, g, redirect, render_template, request, url_for
from app.auth import login_required
from app.db.db import db
from app.db.models import User


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not g.user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def initialize_admin(app):
    @app.get('/admin')
    @admin_required
    def admin_dashboard():
        return render_template('admin_page.html', users=User.query.order_by(User.id).all())

    @app.post('/admin/users/<int:user_id>/status')
    @admin_required
    def admin_user_status(user_id):
        user = db.get_or_404(User, user_id)
        if user.is_admin or user.id == g.user.id:
            abort(400, description='Administrator accounts cannot be disabled here.')
        if request.form.get('active') not in {'true', 'false'}:
            abort(400)
        user.is_active = request.form['active'] == 'true'
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.cli.command('promote-admin')
    @click.argument('username')
    def promote_admin(username):
        """Grant an existing account admin privileges from the server console."""
        user = User.query.filter_by(username=username.strip().lower()).first()
        if user is None:
            raise click.ClickException('Account does not exist.')
        user.is_admin = True
        user.is_active = True
        db.session.commit()
        click.echo(f'Administrator privileges granted to {user.username}.')
