import math

import MySQLdb
import flask
import mysql.connector
from flask import Flask, render_template, request, session, redirect, send_from_directory, flash, url_for
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.dialects import mysql
from werkzeug.utils import secure_filename
from flask_mail import Mail
from datetime import datetime
import json
import os

local_server = True
with open("config.json","r") as c:
    params = json.load(c)["params"]


app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER']= params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']

)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Student(db.Model):
    '''srno,name,email,phone_num,message,date'''
    rno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)


class Posts(db.Model):
    '''srno,name,email,phone_num,message,date'''
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(250), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(250), nullable=True)
    pdf = db.Column(db.String(250), nullable=True)



class Contacts(db.Model):
    '''srno,name,email,phone_num,message,date'''
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def loginuser():
    return render_template('loginuser.html', params=params)

@app.route('/login_validation', methods=['GET', 'POST'])
def login_validation():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pylearn"
    )
    mycursor=mydb.cursor()

    if request.method=='POST':
        loginuser=request.form
        username=str(loginuser.get("username"))
        password=str(loginuser.get("password"))


        if username=="" or password=="":
            flash("Fill all boxes", "warning")
            return redirect('/')

        mycursor.execute("Select * from student where username='"+username+"' and password='"+password+"'")
        r=mycursor.fetchall()
        count=mycursor.rowcount
        if count==1:
            return redirect('/index')
        elif count>1:
            return '<h1>Oops!!<br> Something went wrong</h1>'
        else:
            flash("invalid Email or Password", "danger")
            return redirect('/')
    mydb.commit()
    mycursor.close()
    return render_template("login_validation.html", params=params)


@app.route('/index', methods=['GET', 'POST'])
def index():
    posts = Posts.query.filter_by().all()
    return render_template("index.html", params=params, posts=posts)
    #return render_template("index.html", params=params, posts=posts)

@app.route('/register', methods =['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password==confirm_password:

            '''srno,name,email,phone_num,message,date'''
            entry = Student(name=name, username=username , email=email,password=password)
            db.session.add(entry)
            db.session.commit()
        else:
            flash('Password and Confirm Password do not match ')

    return render_template("registration.html", params=params)


@app.route('/logoutuser')
def logoutuser():
    return redirect("/")
#
# @app.route("/downloads")
# def tos():
#     workingdir = os.path.abspath(os.getcwd())
#     filepath = workingdir + '/static/files/'
#     return send_from_directory(filepath, 'Leena Kirtikar S13 Roll No. 43 Experiment No.1 - Jupyter Notebook.pdf')


@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params, post=post)


@app.route('/contact', methods =['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        '''srno,name,email,phone_num,message,date'''
        entry = Contacts(name=name, phone_num=phone, message=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone + "\n" + email
                          )

    return render_template("contact.html" , params=params)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if ("user" in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template("dashboard.html", params=params, posts=posts)


    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if username == params['admin_user'] and userpass == params['admin_pass']:
            session['user'] = username
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)

    return render_template("login.html", params=params)


# @app.route('/edit/<string:srno>', methods =['GET', 'POST'])
# def edit(srno):
#     if "user" in session and session['user'] == params['admin_user']:
#         if request.method == "POST":
#             title = str(request.form.get("title"))
#             tagline = str(request.form.get("tagline"))
#             slug = str(request.form.get("slug"))
#             content = str(request.form.get("content"))
#             img_file = str(request.form.get("img_file"))
#             date = datetime.now()
#             pdf = request.form.get("pdf")
#
#             if srno=="0":
#                 post = Posts(title=title,tagline=tagline,slug=slug,content=content,img_file=img_file,date = date,pdf=pdf)
#                 db.session.add(post)
#                 db.session.commit()
#                 # f = request.files['file1']
#                 # f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
#                 # workingdir = os.path.abspath(os.getcwd())
#                 # filepath = workingdir + '/static/files/'
#                 # send_from_directory(filepath, pdf)
#                 # return "Uploaded Succesfully"
#             else:
#                 post = Posts.query.filter_by(srno=srno).first()
#                 post.title=str(title)
#                 post.tagline=str(tagline)
#                 post.slug=str(slug)
#                 post.content=str(content)
#                 post.img_file=str(img_file)
#                 post.date = date
#                 post.pdf = pdf
#
#                 db.session.commit()
#                 # f = request.files['file1']
#                 # f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
#                 # workingdir = os.path.abspath(os.getcwd())
#                 # filepath = workingdir + '/static/files/'
#                 # send_from_directory(filepath, post.pdf)
#                 return redirect("/edit/"+srno)
#
#         post = Posts.query.filter_by(srno=srno).first()
#         return render_template("edit.html", params=params, post=post, srno=srno)

@app.route('/edit/<string:srno>', methods =['GET', 'POST'])
def edit(srno):
    if "user" in session and session['user'] == params['admin_user']:
        if request.method == "POST":
            title = request.form.get("title")
            tagline = request.form.get("tagline")
            slug = request.form.get("slug")
            content = request.form.get("content")
            img_file = request.form.get("img_file")
            pdf=request.form.get("pdf")
            date = datetime.now()

            if srno=="0":
                post = Posts(title=title,tagline=tagline,slug=slug,content=content,img_file=img_file,date = date, pdf=pdf)
                db.session.add(post)
                db.session.commit()
                return redirect("/edit/" + srno)
            else:
                post = Posts.query.filter_by(srno=srno).first()
                post.title=title
                post.tagline=tagline
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date = date
                post.pdf = pdf
                db.session.commit()
                return redirect("/edit/"+srno)

        post = Posts.query.filter_by(srno=srno).first()
        return render_template("edit.html", params=params, post=post, srno=srno)

@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if(request.method=='POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)

@app.route('/delete/<string:srno>', methods =['GET', 'POST'])
def delete(srno):
    if "user" in session and session['user'] == params['admin_user']:
        post=Posts.query.filter_by(srno=srno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect("/dashboard")

app.run(debug=True)