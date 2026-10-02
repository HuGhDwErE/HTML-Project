from app.db.db import db
from app.db.models import User, Appeal
from app.tests.test_auth import post, signup


def disable_account(app):
    with app.app_context():
        user = User.query.filter_by(username='dragonborn').one()
        user.is_active = False
        db.session.commit()


def submit(client, message='Please reconsider disabling my account.'):
    token = client.get('/api/session').json['csrf_token']
    return client.post('/appeals', data={'message': message, 'csrf_token': token})


def test_disabled_message_and_appeal_session(client, app):
    assert client.get('/appeals').status_code == 302
    signup(client)
    post(client, '/logout', {})
    disable_account(app)
    wrong = post(client, '/login', {'username': 'dragonborn', 'password': 'wrong'})
    assert 'disabled' not in wrong.json['error']
    assert client.get('/appeals').status_code == 302
    response = post(client, '/login', {'username': 'dragonborn', 'password': ' secret password '})
    assert response.status_code == 401
    assert 'administrator has disabled' in response.json['error']
    assert response.json['appeal_url'] == '/appeals'
    assert client.get('/api/progress').status_code == 401
    assert client.get('/admin').status_code == 302
    assert client.get('/api/session').json['user'] is None
    assert client.post('/appeals', data={'message': 'Please reconsider.'}).status_code == 400
    assert submit(client, 'short').status_code == 400
    assert submit(client).status_code == 302
    assert b'Your appeal has been sent' in client.get('/appeals').data
    assert submit(client).status_code == 400
    with app.app_context():
        assert Appeal.query.count() == 1


def test_appeal_review_and_reenable(client, app):
    signup(client)
    disable_account(app)
    # Existing sessions become appeal-only sessions after the account is disabled.
    assert client.get('/api/session').json['disabled']
    assert b'administrator has disabled' in client.get('/login').data
    assert submit(client, '<script>alert(1)</script> Please reconsider.').status_code == 302
    admin = app.test_client()
    signup(admin, 'moderator')
    assert app.test_cli_runner().invoke(args=['promote-admin', 'moderator']).exit_code == 0
    page = admin.get('/admin')
    assert b'&lt;script&gt;' in page.data
    with app.app_context():
        appeal_id = Appeal.query.one().id
    url = f'/admin/appeals/{appeal_id}/review'
    token = admin.get('/api/session').json['csrf_token']
    assert admin.post(url, data={'decision': 'approved'}).status_code == 400
    assert admin.post(url, data={'decision': 'rejected', 'csrf_token': token}).status_code == 302
    assert b'declined' in client.get('/appeals').data
    assert submit(client, 'Here is more information for my appeal.').status_code == 302
    assert admin.post(url, data={'decision': 'approved', 'csrf_token': token}).status_code == 302
    assert b'Your account is enabled' in client.get('/appeals').data
    assert client.get('/api/progress').status_code == 401
    assert post(client, '/login', {'username': 'dragonborn', 'password': ' secret password '}).status_code == 200
    assert client.get('/api/progress').status_code == 200
    assert admin.post(url, data={'decision': 'rejected', 'csrf_token': token}).status_code == 400


def test_appeals_are_private(client, app):
    signup(client)
    disable_account(app)
    assert submit(client).status_code == 302
    other = app.test_client()
    signup(other, 'another_user')
    assert b'Please reconsider' not in other.get('/appeals').data
    assert submit(other).status_code == 400
    with app.app_context():
        appeal_id = Appeal.query.one().id
    token = other.get('/api/session').json['csrf_token']
    assert other.post(f'/admin/appeals/{appeal_id}/review',
                      data={'decision': 'approved', 'csrf_token': token}).status_code == 403
