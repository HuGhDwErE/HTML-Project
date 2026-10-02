import re
import secrets
from functools import wraps
from flask import g, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from app.db.db import db
from app.db.models import User, Progress


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            if request.path.startswith('/api/'):
                return jsonify(error='Please log in.'), 401
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def initialize_auth(app):
    @app.before_request
    def load_user_and_check_csrf():
        g.user = db.session.get(User, session['user_id']) if session.get('user_id') else None
        if g.user is not None and not g.user.is_active:
            disabled_id = g.user.id
            session.clear()
            session['appeal_user_id'] = disabled_id
            session['disabled_notice'] = True
            g.user = None
        if session.get('user_id') and g.user is None:
            session.clear()
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)
        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token', '')
            if not secrets.compare_digest(session['csrf_token'], token):
                return jsonify(error='Session expired. Refresh the page and try again.'), 400

    @app.context_processor
    def auth_context():
        return dict(current_user=g.user, csrf_token=session['csrf_token'], disabled_notice=session.get('disabled_notice', False))

    @app.get('/api/session')
    def current_session():
        return jsonify(user={'username': g.user.username, 'is_admin': g.user.is_admin} if g.user else None,
                       disabled=session.get('disabled_notice', False),
                       csrf_token=session['csrf_token'])

    def credentials():
        data = request.get_json(silent=True) if request.is_json else request.form
        if not isinstance(data, dict) and not hasattr(data, 'get'):
            return {}, '', ''
        username, password = data.get('username', ''), data.get('password', '')
        if not isinstance(username, str) or not isinstance(password, str):
            return {}, '', ''
        return data, username.strip().lower(), password

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('login_page.html', registering=True)
        data, username, password = credentials()
        if username == 'admin':
            return jsonify(error='This username is reserved. Contact the site owner.'), 400
        if not re.fullmatch(r'[a-z0-9_]{3,80}', username):
            return jsonify(error='Username must contain 3–80 letters, numbers or underscores.'), 400
        if not 8 <= len(password) <= 128:
            return jsonify(error='Password must contain 8–128 characters.'), 400
        if data.get('confirm_password') != password:
            return jsonify(error='Passwords do not match.'), 400
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify(error='Username is already taken.'), 409
        session.clear()
        session['user_id'] = user.id
        session['csrf_token'] = secrets.token_urlsafe(32)
        session.permanent = data.get('remember') is True
        return jsonify(message='Account created.', username=user.username), 201

    dummy_hash = generate_password_hash(secrets.token_urlsafe(32))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login_page.html', registering=False)
        data, username, password = credentials()
        if len(username) > 80 or len(password) > 128:
            return jsonify(error='Incorrect username or password.'), 401
        user = User.query.filter_by(username=username).first()
        valid = check_password_hash(user.password_hash if user else dummy_hash, password)
        if not user or not valid:
            return jsonify(error='Incorrect username or password.'), 401
        if not user.is_active:
            session.clear()
            session['appeal_user_id'] = user.id
            session['disabled_notice'] = True
            session['csrf_token'] = secrets.token_urlsafe(32)
            return jsonify(error='An administrator has disabled your account. You can submit an unban appeal.', appeal_url=url_for('appeals')), 401
        session.clear()
        session['user_id'] = user.id
        session['csrf_token'] = secrets.token_urlsafe(32)
        session.permanent = data.get('remember') is True
        return jsonify(message='Login successful.', username=user.username)

    @app.post('/logout')
    def logout():
        session.clear()
        return jsonify(message='Logged out.')

    @app.route('/api/progress', methods=['GET', 'POST'])
    @login_required
    def progress():
        if request.method == 'GET':
            return jsonify({row.key: row.value for row in Progress.query.filter_by(user_id=g.user.id)})
        data = request.get_json(silent=True)
        allowed = {'collected', 'not-collected', 'completed', 'not-completed',
                   'Breezehome Chest', 'Whiterun Wardrobe', 'Lakeview Manor Chest'}
        if not isinstance(data, dict) or len(data) > 10 or any(
            not isinstance(key, str) or not 1 <= len(key) <= 200 or
            not isinstance(value, str) or value not in allowed for key, value in data.items()
        ):
            return jsonify(error='Invalid progress data.'), 400
        for key, value in data.items():
            row = Progress.query.filter_by(user_id=g.user.id, key=key).first()
            if row is None:
                row = Progress(user_id=g.user.id, key=key)
                db.session.add(row)
            row.value = value
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify(error='Progress changed in another tab. Try again.'), 409
        return jsonify(message='Progress saved.')
