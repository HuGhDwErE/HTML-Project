from datetime import datetime, timezone
from flask import g, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from app.db.db import db
from app.db.models import Appeal, User


def initialize_appeals(app):
    @app.route('/appeals', methods=['GET', 'POST'])
    def appeals():
        user = db.session.get(User, session['appeal_user_id']) if session.get('appeal_user_id') else g.user
        if user is None:
            return redirect(url_for('login'))
        appeal = Appeal.query.filter_by(user_id=user.id).first()
        error = None
        if request.method == 'POST':
            message = request.form.get('message', '').strip()
            if user.is_active:
                error = 'Your account is active. You do not need an unban appeal.'
            elif appeal and appeal.status == 'pending':
                error = 'Your appeal is already waiting for administrator review.'
            elif not 10 <= len(message) <= 2000:
                error = 'Please write an appeal between 10 and 2000 characters.'
            else:
                if appeal is None:
                    appeal = Appeal(user_id=user.id)
                    db.session.add(appeal)
                appeal.message = message
                appeal.status = 'pending'
                appeal.submitted_at = datetime.now(timezone.utc)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    error = 'An appeal was already submitted. Refresh this page.'
                else:
                    return redirect(url_for('appeals'))
        return render_template('appeals_page.html', appeal=appeal, appeal_user=user, error=error), 400 if error else 200
