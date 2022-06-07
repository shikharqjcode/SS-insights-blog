# The file contains the code that can be used to run the website SS-insights
import json
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta, datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import DataRequired


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


local_server = True
app = Flask(__name__)
app.secret_key = "k-3km11ZfOO4D-gfq2Zw3g"
app.permanent_session_lifetime = timedelta(minutes=20)
app.config['UPLOAD_LOC_IMG'] = 'static/img'
app.config['UPLOAD_LOC_PDF'] = 'static/pdf'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = 'True',
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_password']
)

mail = Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# class Contacts(db.Model):
#
#     # sno, name, date, number, email, query
#
#     sno = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     date = db.Column(db.String(12), nullable=True)
#     number = db.Column(db.String(15), nullable=True)
#     email = db.Column(db.String(120), nullable=False)
#     query = db.Column(db.String(120), nullable=True)

class Contactform(db.Model):

    # sno, name, date, number, email, query

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    phone_num = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    query = db.Column(db.String(120), nullable=False)

class Posts(db.Model):

    # sno, title, date, slug, subtext, content, img_file

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(20), nullable=False)
    subtext = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(120), nullable=False)

class Researchposts(db.Model):

    # serialno, title, date, slug, subtext, content, img_file, cont

    serialno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(20), nullable=False)
    img_file = db.Column(db.String(120), nullable=False)
    pdf_file = db.Column(db.String(120), nullable=False)
    cont = db.Column(db.String(120), nullable=False)
    subtext = db.Column(db.String(120), nullable=False)
    content = db.Column(db.String(120), nullable=False)

todays_date = date.today()
year = todays_date.year

@app.route("/sample")
def sample():
    return render_template('layout.html', title='Sample', year=year)

@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method=="POST":
        # Add entry to the database
        name = request.form.get('name')
        email = request.form.get('email')
        phone_num = request.form.get('phone_num')
        query = request.form.get('query')
        entry = Contactform(name=name, date=datetime.now(), phone_num=phone_num, email=email, query=query)
        db.session.add(entry)
        db.session.commit()
        flash("Query Submitted Successfully!", "info")

    return render_template('home.html', title='Home', year=year)

@app.route("/blogs")
@app.route("/blog")
def blog():
    blogs = Posts.query.filter_by().all()
    return render_template('blog.html', title='Blogs', blogs=blogs, year=year)

@app.route("/blog/<string:blog_slug>", methods=['GET'])
def blogpost(blog_slug):
    post = Posts.query.filter_by(slug=blog_slug).first()
    return render_template('blogpost.html', title=post.title, post=post, year=year)

@app.route("/Research")
@app.route("/research")
def research():
    resposts = Researchposts.query.filter_by().all()
    return render_template('research.html', title='Research', resposts=resposts, year=year)

@app.route("/research/<string:res_slug>", methods=['GET'])
def respostpage(res_slug):
    researchpage = Researchposts.query.filter_by(slug=res_slug).first()
    return render_template('respage.html', title=researchpage.title, research=researchpage, year=year,
                           cont=researchpage.cont)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST" and request.form['nm'] == params['admin-user'] and \
            request.form['ps'] == params['admin-password']:
        session.permanent = True
        usr = request.form["nm"]
        session["user"] = usr
        return redirect(url_for('user'))
    else:
        if "user" in session:
            return redirect(url_for("user"))

        return render_template('login.html', title='Login Page', year=year)

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        posts = Posts.query.filter_by().all()
        resps = Researchposts.query.filter_by().all()
        return render_template('dashboard.html', username=user, title="Dashboard", year=year,
                               posts=posts, resps=resps)
    else:
        return redirect(url_for("login"))


class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

@app.route("/upload_img", methods = ['GET', 'POST'])
def upload_img():
    if ("user" in session and session['user'] == params['admin-user']):
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data #first grab the file
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_LOC_IMG'], secure_filename(file.filename))) #then save the file
            flash("Image has been uploaded successfully", "info")
        return render_template("upload_img.html", form=form)

@app.route("/upload_pdf", methods = ['GET', 'POST'])
def upload_pdf():
    if ("user" in session and session['user'] == params['admin-user']):
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data #first grab the file
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_LOC_PDF'], secure_filename(file.filename))) #then save the file
            flash("PDF has been uploaded successfully", "info")
        return render_template("upload_pdf.html", form=form)

@app.route("/edit-blog/<string:sno>", methods=['GET', 'POST'])
def edit_blog(sno):
    if ("user" in session and session['user'] == params['admin-user']):
        if request.method == "POST":
            box_title = request.form.get('title')
            subtext = request.form.get('subtext')
            slug = request.form.get('slug')
            img_file = request.form.get('img_file')
            content = request.form.get('content')
            date = datetime.now()

            blog = Posts.query.filter_by(sno=sno).first()
            blog.title = box_title
            blog.date = date
            blog.slug = slug
            blog.img_file = img_file
            blog.subtext = subtext
            blog.content = content
            db.session.commit()
            flash("Change has been made", "info")
            return redirect('/edit-blog/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit_blog.html', params=params, post=post, sno=sno)

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    img_file = StringField("Img_File", validators=[DataRequired()])
    subtext = StringField("Subtext", validators=[DataRequired()])
    content = SubmitField("Content", validators=[DataRequired()])

@app.route("/add-post", methods=['GET', 'POST'])
def add_blog():
    if ("user" in session and session['user'] == params['admin-user']):

        title = request.form.get('title')
        subtext = request.form.get('subtext')
        slug = request.form.get('slug')
        img_file = request.form.get('img_file')
        content = request.form.get('content')
        date = datetime.now()

        blog = Posts(title = title, date=date, slug=slug, img_file=img_file, subtext=subtext, content=content)

        db.session.add(blog)
        db.session.commit()

        flash("Blog has been added", "info")

    return render_template('add_blog.html', year=year)

@app.route("/edit-res/<string:serialno>", methods=['GET', 'POST'])
def edit_res(serialno):
    if ("user" in session and session['user'] == params['admin-user']):
        if request.method == "POST":
            res_title = request.form.get('title')
            subtext = request.form.get('subtext')
            slug = request.form.get('slug')
            img_file = request.form.get('img_file')
            pdf_file = request.form.get('pdf_file')
            content = request.form.get('content')
            cont = request.form.get('cont')
            date = datetime.now()

            respost = Researchposts.query.filter_by(serialno=serialno).first()
            respost.title = res_title
            respost.date = date
            respost.slug = slug
            respost.cont = cont
            respost.img_file = img_file
            respost.pdf_file = pdf_file
            respost.subtext = subtext
            respost.content = content
            db.session.commit()
            return redirect('/edit-res/' + serialno)
        respost = Researchposts.query.filter_by(serialno=serialno).first()
        return render_template('edit_res.html', params=params, respost=respost, serialno=serialno)

@app.route("/delete-blog/<string:sno>")
def delete_blog(sno):
    if ("user" in session and session['user'] == params['admin-user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for("user"))

@app.route("/delete-res/<string:serialno>")
def delete_res(serialno):
    if ("user" in session and session['user'] == params['admin-user']):
        respost = Researchposts.query.filter_by(serialno=serialno).first()
        db.session.delete(respost)
        db.session.commit()
    return redirect(url_for("user"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been successfully logged out!", "info")
    return redirect(url_for("login"))


# @app.route("/main")
# def main():
#     return render_template('main.html', title='Sample')

if __name__ == "main":
    app.run(debug=True)


# set FLASK_APP=webrun
# set FLASK_ENV=development
# flask run