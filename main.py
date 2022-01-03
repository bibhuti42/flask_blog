from flask import Flask, app, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import json
import os
import math

json_file = open('config.json')
params = json.load(json_file)

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload-location']

# app.config.update(
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = '465',
#     MAIL_USER_SSL = True,
#     MAIL_USERNAME = params['gmail-username'],
#     MAIL_PASSWORD = params['gmail-password']
# )

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'bibhutisahoo52@gmail.com'
app.config['MAIL_PASSWORD'] = 'tourist@123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_blog'
db = SQLAlchemy(app)

class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(20), nullable=False)
    img_file = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.String(12), nullable=True)

@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_post']))
    page = request.args.get('page')

    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_post']) : (page-1)*int(params['no_post'])+int(params['no_post'])]

    if(page == 1):
        prev = '#'
        next = '/?page='+ str(page + 1)
    elif(page == last):
        prev = '/?page='+ str(page - 1)
        next = '#'
    else:
        prev = '/?page='+ str(page - 1)
        next = '/?page='+ str(page + 1)
    
    return render_template('index.html', posts = posts, prev=prev, next = next)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):

    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', posts = post)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        records = Contacts(name = name, email=email, phone = phone, message=message, created_at=datetime.now())
        db.session.add(records)
        db.session.commit()

        # mail.send_message('New message from Flask', sender=email, recipients=params['gmail-username'], body = message)
        msg = Message(subject = "hello", body = "hello", sender = "bibhutisahoo52@gmail.com", recipients = ["bibhutisahoo42@quocent.com"])
        mail.send(msg)
    return render_template('contact.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    posts = Posts.query.all()
    if 'user' in session and session['user'] == params['admin-user']:
        return render_template('dashboard.html', posts=posts)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == params['admin-user'] and password == params['admin-password']:
            session['user'] = username
            return render_template('dashboard.html', posts=posts)
        else:
            return 'invalid username or password'
    
    return render_template('login.html')

@app.route('/edit/<string:sno>', methods=['GET','POST'])
def edit(sno):
    if request.method == 'POST':
        title = request.form.get('title')
        tagline = request.form.get('tagline')
        slug = request.form.get('slug')
        content = request.form.get('content')
        img_file = request.form.get('img_file')
        date = datetime.now()

        if sno == '0':
            post = Posts(title=title, tagline=tagline, slug = slug, content = content, img_file = img_file, created_at = date)
            db.session.add(post)
            db.session.commit()

        else:
            post = Posts.query.filter_by(id=sno).first()
            post.title = title
            post.tagline = tagline
            post.slug = slug
            post.content = content
            post.img_file = img_file
            db.session.commit()
            return redirect('/edit/'+sno)
    post = Posts.query.filter_by(id=sno).first()
    return render_template('edit.html', post=post)

@app.route('/uploader', methods=['GET','POST'])
def uploader():
    
    if request.method == 'POST':
        f = request.files['img_file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return 'Uploaded successfuly!'

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route('/delete/<string:sno>', methods=['GET','POST'])
def delete(sno):
    
    post = Posts.query.filter_by(id=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)