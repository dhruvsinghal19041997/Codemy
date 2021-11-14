from flask import Flask, request, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask import Flask, render_template,request,url_for,flash,redirect,abort
import json
app = Flask(__name__)

mail = Mail(app)

with open('config.json','r') as c:
    params= json.load(c)["params"]
def send_confirmation_email():
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    email = 'singhaldhruv5@rediffmail.com'
    token = confirm_serializer.dumps(email, salt='email-confirm')
    msg = Message('Confirm Email', sender=params['gmail_user'], recipients=[email])
    link = url_for('confirm_email', token=token, _external=True)
    msg.html(render_template('emailconfirmation'))
    mail.send(msg)



@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))

        user = User.query.filter_by(email=email).first()

    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.email_confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Thank you for confirming your email address!')

    return redirect(url_for('recipes.index'))

def main():
    send_confirmation_email()

