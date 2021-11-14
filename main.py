from flask import Flask, render_template,request,url_for,flash,redirect,abort
import bcrypt
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail,Message
from datetime import date
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager,login_required,login_user,
                         UserMixin,logout_user,current_user)
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import math
from sqlalchemy import func
from validate_email import validate_email

import re

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

post_slug=''
error=''
with open('config.json','r') as c:
    params= json.load(c)["params"]
local_server=params['local_uri']
application=app=Flask(__name__)
app.secret_key = b'\x06\xb8f\xc2\xdd\xbcz\xda'
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
REMEMBER_COOKIE_SECURE=True
bcrypt = Bcrypt(app)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_app_password']
)

mail=Mail(app)

app.config['SECRET_KEY']=app.secret_key

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI']=params['local_uri']
    app.config['MYSQL_PORT']=3306
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db=SQLAlchemy(app)

class Comments(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    comment=db.Column(db.String(150),unique=False,nullable=False)
    pid=db.Column(db.Integer,unique=False,nullable=False)
    author=db.Column(db.Integer, unique=False,nullable=False)
    date=db.Column(db.Date,unique=False,nullable=False)

class Contact(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(20),unique=False,nullable=False)
    email = db.Column(db.String(40), unique=False, nullable=False)
    phone_number = db.Column(db.Integer, unique=False, nullable=False)
    message = db.Column(db.String(100), unique=False, nullable=False)

class Posts(db.Model):
    pid=db.Column(db.Integer, db.ForeignKey('comments.pid'), primary_key=True)
    title=db.Column(db.String(50),unique=False,nullable=False)
    slug = db.Column(db.String(30), unique=False, nullable=False)
    postviews=db.Column(db.Integer,unique=False,nullable=True)
    content = db.Column(db.String(100), unique=False, nullable=False)
    date = db.Column(db.String(10), unique=False, nullable=False)
    username=db.Column(db.String(30),unique=False,nullable=False)
    comments = db.relationship('Comments',
                               backref=db.backref('posts', lazy=True))


class NewPost(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),unique=False,nullable=False)
    content=db.Column(db.String(100000),unique=False,nullable=False)
    date=db.Column(db.Date,unique=False,nullable=True)

class New_user(db.Model,UserMixin):
    userid=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(30),unique=True,nullable=False)
    email=db.Column(db.String(30),unique=False,nullable=False)
    password=db.Column(db.String,unique=False,nullable=False)
    confirmed=db.Column(db.Boolean,nullable=False,default=False)

    def get_id(self):
        return (self.userid)


@app.context_processor
def utility_processor():
    def format_price(text):
        return TAG_RE.sub('', text)
    return dict(format_price=format_price)


@login_manager.user_loader
def load_user(user_id):
    return New_user.query.get(int(user_id))

@app.route('/new_post', methods=['GET','POST'])
@login_required
def new_post( ):
    if request.method=='POST':
        post_id = Posts.query.order_by(Posts.pid.desc()).first()
        print(post_id)
        html = request.form.get('editordata')
        title=request.form.get('title')
        post_id=post_id.pid
        post_id+=1
        if html!='':
            newpost=Posts(pid=post_id,title=title,slug=title.replace(" ","_"),content=html,date=date.today(),username=current_user.username)
            db.session.add(newpost)
            db.session.commit()
            flash('New Post has been successfully added !!')
            return redirect(url_for('home_page'))
        else:
            flash('Content cannot be empty')
            return redirect(url_for('new_post'))
    return render_template('new_post.html',params=params)


@app.route('/')
@app.route('/home')
def home_page():
    posts = Posts.query.order_by(Posts.date.desc()).all()
    posts2 = db.session.query(Posts.pid,Posts.date,Posts.title,Posts.username,Posts.content,Posts.postviews,Posts.slug,func.count(Comments.cid).label('com_count') ) \
        .outerjoin(Comments) \
        .group_by(Posts.pid).all()
    print(posts2)
    # posty=Posts.query(Posts, func.count(Comments.cid)) \
    #     .join(Comments) \
    #     .filter(Posts.pid == Comments.pid).group_by(Comments.pid).all()

    # posty= db.session.query(Posts, func.count(Comments.cid))\
    # .select_from(Comments)\
    # .join(comments.pid)\
    # .group_by(Comments.cid)
    #print("posty"+str(posts2))
    print('Post:'+ str(posts2))
    #print(posts)
    last=math.ceil(len(posts)/params['post_count'])
    page = request.args.get('page')
    if current_user.is_authenticated:
        if not current_user.confirmed:
            flash("Please confirm your account. ")

    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['post_count']):(page-1)*int(params['post_count'])+int(params['post_count'])]
    if page==1:
        next='/?page='+str(page+1)
        prev='#'
    elif (page==last):
        prev = '/?page=' + str(page - 1)
        next = '#'
    else:
        prev = '/?page=' + str(page - 1)
        next = '/?page=' + str(page + 1)
    last=str(last)
    print(last)
    print(prev)
    print(next)
    return render_template('home.html',params=params,posts=posts2,remove_tags=remove_tags,prev=prev,next=next,last=last)

@app.route('/about')
def about_me():
    return render_template('about_me.html',params=params)

@app.route('/search_results', methods=['GET','POST'])
def search_results():
    #if (request.method == 'POST'):
    search_query=str(request.form.get('search_data')).lower().split()
    posts = Posts.query.filter(func.lower(Posts.title).contains(search_query)).all()
    last = math.ceil(len(posts) / params['post_count'])
    page = request.args.get('page')
    if current_user.is_authenticated:
        if not current_user.confirmed:
            flash("Please confirm your account. ")

    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[
            (page - 1) * int(params['post_count']):(page - 1) * int(params['post_count']) + int(params['post_count'])]
    if page == 1:
        next = '/?page=' + str(page + 1)
        prev = '#'
    elif (page == last):
        prev = '/?page=' + str(page - 1)
        next = '#'
    else:
        prev = '/?page=' + str(page - 1)
        next = '/?page=' + str(page + 1)
    last = str(last)
    print(last)
    print(prev)
    print(next)
    return render_template('home.html',params=params,posts=posts,remove_tags=remove_tags,prev=prev,next=next,last=last)

@app.route('/contact',methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        entry=Contact(name=name,email=email,phone_number=phone,message=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from'+name,
                          sender=email,
                          recipients=[params['gmail_user']],
                          body=message+"\n"+phone)
        flash('Message sent successfully.')
    return render_template('contact.html',params=params)
@app.route("/post")
@app.route("/post/<string:post_slug>",methods=['GET'])
def posts(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    post.postviews+=1
    db.session.add(post)
    db.session.commit()
    comments=Comments.query.filter_by(pid=post.pid)
    return render_template('posts.html',params=params,post=post,comments=comments)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    if request.method=='POST':
        user=New_user()
        saved_pass=New_user.query.filter_by(username=request.form.get('uname')).first()
        current_pass=request.form.get('password')
        if  New_user.query.filter_by(username=request.form.get('uname')).first()  and \
                bcrypt.check_password_hash(saved_pass.password,current_pass):
            login_user(New_user.query.filter_by(username=request.form.get('uname')).first())
            flash("You are now logged in !!")
            return redirect(url_for('home_page'))
        else:
            flash('Invalid Credentials')
            return render_template('login.html', params=params)

    else:
        error=''
        return render_template('login.html', params=params, error=error)

@app.route('/register',methods=['GET','POST'])
def registeration():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    uname=request.form.get('uname')
    email=request.form.get('email')
    passw=request.form.get('pass')
    cpass=request.form.get('cpass')
    data = New_user.query.filter_by(username=uname).first()
    if request.method=='POST':
        encrypt_pass = bcrypt.generate_password_hash(passw)
        if data==None:
            newuser=New_user(username=uname,email=email,password=encrypt_pass,confirmed=False)
            if len(passw)>15:
                flash('Password must contain less than 15 characters')
                if cpass!=passw:
                    flash('Password does not match')
                    return redirect(url_for('registeration'))
                return redirect(url_for('registeration'))
            else:
                if cpass!=passw:
                    flash('Password does not match')
                    return redirect(url_for('registeration'))
                else:
                        db.session.add(newuser)
                        db.session.commit()
                        send_confirmation_email(email,uname)
                        flash('Registeration Successfull. Confirmation mail has been sent to '+email)
                        return redirect(url_for('dashboard'))
                return redirect(url_for('registeration'))
            flash('Registeration Successfull. You can now login!!')
            return redirect(url_for('dashboard'))
        else:
            flash('username already exist')
            if len(passw)>15:
                flash('Password must contain less than 15 characters')
                if cpass!=passw:
                    flash('Password does not match')
            else:
                if cpass!=passw:
                    flash('Password does not match')
            return redirect(url_for('registeration'))
    return render_template('register.html', params=params)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out !!')
    return redirect(url_for('dashboard'))

@app.route('/myposts')
@login_required
def mypost():
    posts=Posts.query.filter_by(username=current_user.username).all()
    return render_template('mypost.html',params=params,posts=posts)

@login_required
@app.route('/delete/<string:pid>',methods=['GET','POST'])
def deletepost(pid):
    post=Posts.query.filter_by(pid=pid).first()
    if post.username != current_user.username:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted successfully !!')
    return redirect(url_for('mypost'))

@app.errorhandler(401)
def forbidden(e):
    return render_template('unauthorized.html'), 401


@app.errorhandler(500)
def forbidden(e):
    return render_template('notfound.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('forbidden.html'), 403

@app.errorhandler(404)
def forbidden(e):
    return render_template('notfound.html'), 404


@login_required
@app.route('/edit/<string:pid>',methods=['GET','POST'])
def editpost(pid):
    post=Posts.query.filter_by(pid=pid).first()
    if post.username!=current_user.username:
        abort(403)
    if request.method=='POST':
        post.title=request.form.get('title')
        post.content=request.form.get('editordata')
        db.session.commit()
        flash('Post has been updated successfully !!')
        return redirect(url_for('mypost'))
    return render_template('editpost.html', params=params, post=post)

def send_confirmation_email(email,uname):
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = confirm_serializer.dumps(uname)
    msg = Message('Confirm Email', sender=params['gmail_user'], recipients=[email])
    link = url_for('confirm_email', token=token,_external=True)
    msg.html=render_template('confirmation_mail.html',link=link,username=uname)
    mail.send(msg)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        uname = confirm_serializer.loads(token, max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('dashboard'))
    user = New_user.query.filter_by(username=uname).first()

    if user.confirmed:
        if current_user:
            flash('Account already confirmed.')
            return redirect(url_for('home_page'))
        else:
            flash('Account already confirmed. Please login.')
            return redirect(url_for('dashboard'))
    else:
        user.confirmed = True
        db.session.commit()
        if current_user:
            flash('Thank you for confirming your email address!')
            return redirect(url_for('home_page'))
        else:
            flash('Thank you for confirming your email address!')
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route('/resend')
@login_required
def resend_confirmation():
    send_confirmation_email(current_user.email,current_user.username)
    flash('A new confirmation email has been sent.')
    return redirect(url_for('home_page'))

@app.route('/pass_reset')
def pass_reset():
   return render_template('password_reset.html',params=params)

@app.route('/reset_password',methods=['GET','POST'])
def reset_link():
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        uname = request.form.get('uname')
        token = confirm_serializer.dumps(uname,salt='reset_pass')
        email=New_user.query.filter_by(username=uname).first().email
        msg = Message('Password Reset', sender=params['gmail_user'], recipients=[email])
        link = url_for('reset_password', token=token,_external=True)
        msg.html=render_template('reset_template.html',link=link,username=uname)
        print(token)
        mail.send(msg)
        flash('Password Reset link sent to '+email)
        return redirect(url_for('dashboard'))
    except AttributeError:
        flash('Invalid Username')
        return redirect(url_for('pass_reset'))


@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        print(token)
        uname = confirm_serializer.loads(token, salt='reset_pass',max_age=3600)
        print(uname)
        user = New_user.query.filter_by(username=uname).first()
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
    if request.method=='POST':
        passw=request.form.get('pass')
        cpass=request.form.get('cpass')
        if passw==cpass:
            encrypt_pass = bcrypt.generate_password_hash(passw)
            user.password=encrypt_pass
            db.session.commit()
            flash('Password updated successfully !!')
            return redirect(url_for('dashboard'))
    return render_template('new_pass.html',params=params,token=token)

@app.route('/post/<pid>/postcomment',methods=['GET','POST'])
@login_required
def postcomment(pid):
    if request.method=='POST':
        comment=request.form.get('comment')
        author=New_user.query.filter_by(username=current_user.username).first().username
        post_slug=Posts.query.filter_by(pid=pid).first().slug
        postcomment=Comments(comment=comment,pid=pid,author=author,date=date.today())
        db.session.add(postcomment)
        db.session.commit()
        flash('Your comment has been posted successfully')
        return redirect(url_for('posts',post_slug=post_slug))

if(__name__=="__main__"):
    app.run(debug=True ,port=5003)

