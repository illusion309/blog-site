from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField, upload_success, upload_fail
from datetime import date
import os


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
ckeditor = CKEditor(app)
Bootstrap(app)


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/img/<path:filename>')
def serve_audio(filename):
    return send_from_directory('img/', filename)

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.save(os.path.join('./img', f.filename))
    url = url_for('serve_audio', filename=f.filename)
    return upload_success(url=url)  # return upload_success call


@app.route('/')
def get_all_posts():
    posts =  BlogPost.query.all()
    # print(posts)
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    posts =  BlogPost.query.all()
    # print(posts)
    for blog_post in posts:
        if blog_post.id == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/edit-post/<int:post_id>", methods = ['GET', 'POST'])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    form = CreatePostForm(
            title = post.title,
            subtitle = post.subtitle,
            author = post.author,
            body = post.body,
            img_url = post.img_url
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.author = form.author.data
        post.body = form.body.data
        post.img_url = form.img_url.data
        db.session.commit()
        return redirect(url_for('show_post', index=post_id))
    return render_template("make-post.html", form = form, is_edit=True)


@app.route("/new-post", methods = ['GET', 'POST'])
def new_post():
    form = CreatePostForm()

    if form.validate_on_submit():
        newBlogPost =  BlogPost(
                        title = form.title.data,
                        subtitle = form.subtitle.data,
                        date = date.today().strftime("%B %d, %Y"),
                        body = form.body.data,
                        author = form.author.data,
                        img_url = form.img_url.data)

        db.session.add(newBlogPost)
        db.session.commit()
        print(date.today().strftime("%B %d, %Y"))
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form = form)

@app.route("/deleted/<int:post_id>")
def delete(post_id):
    post = BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))
    


#if __name__ == "__main__":
 #   app.run(debug=True, port=8080)