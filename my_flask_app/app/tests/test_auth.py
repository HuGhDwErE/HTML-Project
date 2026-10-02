from werkzeug.security import check_password_hash
from app.db.db import db
from app.db.models import User


def post(client, url, data):
    token = client.get('/api/session').json['csrf_token']
    return client.post(url, json=data, headers={'X-CSRF-Token': token})


def signup(client, username='dragonborn', password=' secret password '):
    return post(client, '/register', dict(username=username, password=password, confirm_password=password))


def test_register_login_logout(client, app):
    assert signup(client).status_code == 201
    with app.app_context():
        user = User.query.one()
        assert user.password_hash != ' secret password '
        assert check_password_hash(user.password_hash, ' secret password ')
    assert client.get('/api/session').json['user']['username'] == 'dragonborn'
    assert client.get('/storage').status_code == 200
    assert post(client, '/logout', {}).status_code == 200
    assert client.get('/storage').status_code == 302
    assert post(client, '/login', dict(username='Dragonborn', password='wrong')).status_code == 401
    assert post(client, '/login', dict(username='Dragonborn', password=' secret password ', remember=True)).status_code == 200
    with client.session_transaction() as session:
        assert session.permanent


def test_duplicate_and_validation(client):
    assert signup(client).status_code == 201
    assert signup(client, 'DRAGONBORN').status_code == 409
    assert signup(client, 'invalid name').status_code == 400
    assert signup(client, 'valid_name', 'short').status_code == 400
    assert post(client, '/register', dict(username='valid_name', password='longpassword', confirm_password='different')).status_code == 400
    assert post(client, '/login', {'username': [], 'password': {}}).status_code == 401


def test_csrf_and_session_rotation(client):
    old_token = client.get('/api/session').json['csrf_token']
    assert client.post('/register', json={}).status_code == 400
    assert signup(client).status_code == 201
    assert client.post('/logout', json={}, headers={'X-CSRF-Token': old_token}).status_code == 400
    assert client.get('/logout').status_code == 405


def test_progress_is_private_and_persistent(client, app):
    assert client.get('/api/progress').status_code == 401
    signup(client)
    assert post(client, '/api/progress', {'Wabbajack': 'collected'}).status_code == 200
    assert client.get('/api/progress').json == {'Wabbajack': 'collected'}
    post(client, '/logout', {})
    signup(client, 'other_user')
    assert client.get('/api/progress').json == {}
    assert post(client, '/api/progress', {'item': 'invalid'}).status_code == 400
    post(client, '/logout', {})
    post(client, '/login', dict(username='dragonborn', password=' secret password '))
    assert client.get('/api/progress').json == {'Wabbajack': 'collected'}


def test_pages(client):
    assert b'Create account' in client.get('/register').data
    assert b'login-form' in client.get('/login').data
    assert client.get('/api/v1/main/').json == {'data': {'message': 'Hello, World!'}}


def test_deleted_user_session(client, app):
    signup(client)
    with app.app_context():
        db.session.delete(User.query.one())
        db.session.commit()
    assert client.get('/api/session').json['user'] is None
    assert client.get('/api/progress').status_code == 401


def test_database_survives_restart(tmp_path):
    from app.app import create_app
    config = dict(TESTING=True, SECRET_KEY='test-only-secret',
                  SQLALCHEMY_DATABASE_URI='sqlite:///' + (tmp_path / 'accounts.db').as_posix())
    first = create_app(config)
    client = first.test_client()
    assert signup(client).status_code == 201
    assert post(client, '/api/progress', {'storage:Wabbajack': 'Breezehome Chest'}).status_code == 200
    with first.app_context():
        db.session.remove()
        db.engine.dispose()
    second = create_app(config)
    client = second.test_client()
    assert post(client, '/login', dict(username='dragonborn', password=' secret password ')).status_code == 200
    assert client.get('/api/progress').json == {'storage:Wabbajack': 'Breezehome Chest'}
