import sqlite3
from app.db.db import db
from app.db.models import User
from app.tests.test_auth import post, signup
from werkzeug.security import generate_password_hash


def test_admin_access_and_reserved_name(client):
    assert client.get('/admin').status_code == 302
    assert signup(client, 'ADMIN').status_code == 400
    assert signup(client).status_code == 201
    assert client.get('/admin').status_code == 403
    assert post(client, '/register', dict(username='hacker', password='password123',
                confirm_password='password123', is_admin=True)).status_code == 201
    assert client.get('/api/session').json['user']['is_admin'] is False
    token = client.get('/api/session').json['csrf_token']
    assert client.post('/admin/users/1/status', data={'active': 'false', 'csrf_token': token}).status_code == 403


def test_admin_can_disable_and_enable_users(client, app):
    signup(client)
    with app.app_context():
        target_id = User.query.one().id
        admin = User(username='admin', password_hash=generate_password_hash('admin-password'))
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
    result = app.test_cli_runner().invoke(args=['promote-admin', 'ADMIN'])
    assert result.exit_code == 0
    admin_client = app.test_client()
    post(admin_client, '/login', dict(username='ADMIN', password='admin-password'))
    response = admin_client.get('/admin')
    assert response.status_code == 200
    assert b'password_hash' not in response.data and b'scrypt:' not in response.data
    url = f'/admin/users/{target_id}/status'
    assert admin_client.post(url, data={'active': 'false'}).status_code == 400
    token = admin_client.get('/api/session').json['csrf_token']
    assert admin_client.post(url, data={'active': 'false', 'csrf_token': token}).status_code == 302
    assert client.get('/api/session').json['user'] is None
    assert client.get('/api/progress').status_code == 401
    assert post(client, '/login', dict(username='dragonborn', password=' secret password ')).status_code == 401
    assert admin_client.post(url, data={'active': 'true', 'csrf_token': token}).status_code == 302
    assert post(client, '/login', dict(username='dragonborn', password=' secret password ')).status_code == 200
    assert admin_client.post(f'/admin/users/{admin_id}/status',
                            data={'active': 'false', 'csrf_token': token}).status_code == 400
    # Revoking privileges in the database also affects an existing session.
    with app.app_context():
        db.session.get(User, admin_id).is_admin = False
        db.session.commit()
    assert admin_client.get('/admin').status_code == 403


def test_existing_database_upgrade(tmp_path):
    from app.app import create_app
    path = tmp_path / 'old.db'
    password_hash = generate_password_hash('old-password')
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(80) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL)')
        connection.execute('INSERT INTO users VALUES (1, ?, ?)', ('admin', password_hash))
    app = create_app(dict(TESTING=True, SECRET_KEY='test', SQLALCHEMY_DATABASE_URI='sqlite:///' + path.as_posix()))
    with app.app_context():
        user = db.session.get(User, 1)
        assert user.password_hash == password_hash
        assert user.is_active and not user.is_admin
    assert app.test_cli_runner().invoke(args=['promote-admin', 'ADMIN']).exit_code == 0
    # Repeating startup must preserve the role and existing account.
    app = create_app(dict(TESTING=True, SECRET_KEY='test', SQLALCHEMY_DATABASE_URI='sqlite:///' + path.as_posix()))
    with app.app_context():
        assert db.session.get(User, 1).is_admin
