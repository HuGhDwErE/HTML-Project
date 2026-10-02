# Login and database setup

Run from `my_flask_app`:

```powershell
.\.venv\Scripts\python.exe run.py
```

Open http://127.0.0.1:5000/register to create an account. Usernames contain
3–80 letters, numbers or underscores and are case-insensitive. Passwords
contain 8–128 characters; spaces are preserved. Remember me lasts 30 days.

SQLite tables are created automatically. Development data lives in
`instance/development.db`; the generated development signing key lives in
`instance/secret.key`. Keep both files to preserve accounts and sessions.
Tests use an isolated in-memory database.

The application saves item collection, quest completion and storage locations
separately for each account. Browsing items and quests is public; saving requires
login. Storage requires login. Old browser-only accounts must register again;
old plaintext credentials are removed from browser storage when the page loads.

To install all dependencies, including semantic search:

```powershell
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

Search loads its model on the first search and may download it. The login and
tracker pages work without the optional search dependencies installed.

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest app/tests app/modules/main/main_tests.py -q
```

For production, set a strong random `SECRET_KEY` and serve over HTTPS. Optionally
set `DATABASE_URL` to another SQLAlchemy database URI and install its driver.
Production defaults to `instance/production.db`. Never commit the database,
secret key or `.env` file. Existing table schema changes require migrations;
startup creates missing tables but does not alter existing ones.

Authentication uses Werkzeug password hashes, signed HttpOnly session cookies,
CSRF tokens for state-changing requests and Secure cookies in production,
following Flask's security guidance:
https://flask.palletsprojects.com/en/stable/web-security/

Email verification, forgotten-password email delivery, and login rate limiting
are not included in this implementation.

## Account administration

The existing ADMIN account (stored as admin) has been promoted in the local
development database. Log in with its existing password and open /admin or the
home page's Manage accounts link. Administrators can view IDs, usernames, roles
and status, and enable or disable regular accounts. Passwords and hashes are
not displayed. Administrator accounts cannot be disabled from this page.
Disabled accounts lose access on their next request.

Roles are checked in the database on every request. Public registration cannot
grant administrator privileges and the admin username is reserved. To promote
an existing account in another database, run from the server console:

```powershell
.\.venv\Scripts\python.exe -m flask --app run:app promote-admin USERNAME
```

Startup adds is_admin and is_active columns to older account tables while
preserving existing users and hashes. A username alone never grants privileges.
The local promotion does not change a separate production database.

Account records are in the users table in instance/development.db. Open this
SQLite file in a database viewer to inspect records. The password_hash column
contains salted scrypt hashes, not readable passwords. Keep the database private;
hashing passwords does not encrypt usernames or other database data.
