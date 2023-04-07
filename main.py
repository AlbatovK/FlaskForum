import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, redirect, request, abort, url_for
from flask import render_template
from flask_apispec import FlaskApiSpec
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask_restful import Api
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from api import user_resource
from data import db_session
from data.post import Post
from data.tag import Tag
from data.thread_message import ThreadMessage
from data.user import User
from forms.image_load_form import ImageLoadForm
from forms.login import LoginForm
from forms.message import MessageForm
from forms.post_add import AddPostForm
from forms.post_edit import EditPostForm
from forms.register import RegisterForm

app = Flask(__name__)
api = Api(app)

api.add_resource(user_resource.UserResource, '/api/v2/user/<int:user_id>')
api.add_resource(user_resource.UserListResource, '/api/v2/users')

spec = APISpec(
    title='FlaskForum',
    version='v2',
    plugins=[MarshmallowPlugin()],
    openapi_version='2.0.0',
    info={
        "description": "📝 Api endpoints for FlaskForum Web App",
        "version": "2.0.0",
        "title": "FlaskForum REST API",
        "contact": {
            "email": "albatovkonstantin@gmail.com"
        },
    }
)

app.config.update(
    {
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',
        'APISPEC_SPEC': spec
    }
)

docs = FlaskApiSpec(app)
docs.register(user_resource.UserResource)
docs.register(user_resource.UserListResource)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Данная почта уже используется.")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь с таким именем уже зарегистрирован.")

        user = User(name=form.name.data, email=form.email.data, about=form.about.data)

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/user/<int:user_id>')
def user_page(user_id):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    rating = sum([x.rating for x in user.posts])
    avatar_url = url_for('static', filename=f'img/{user.avatar if user.avatar else "profile.png"}')
    return render_template('user.html', user=user,
                           rating=rating, posts=user.posts, title=user.name, avatar_url=avatar_url)


@app.route('/load_avatar/<int:user_id>', methods=['GET', 'POST'])
@login_required
def load_avatar(user_id):
    form = ImageLoadForm()
    if form.validate_on_submit():
        if form.file_name.data:
            file = request.files[form.file_name.name]
            file_name = secure_filename(file.filename)
            file.save(f'static/img/{file_name}')

            session = db_session.create_session()
            user = session.query(User).filter(User.id == user_id).first()
            user.avatar = file_name
            session.commit()
        return redirect(f'/user/{user_id}')

    return render_template("file_upload.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html', message="Неправильный логин или пароль", form=form)

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/posts', methods=['GET', 'POST'])
@login_required
def add_post():
    form = AddPostForm()
    if not form.tags.choices:
        add_session = db_session.create_session()
        all_tags = add_session.query(Tag).all()
        form.tags.choices = [(tag.id, tag.name) for tag in all_tags]

    if form.validate_on_submit():
        add_session = db_session.create_session()
        tag_ids = [int(x) for x in form.tags.data]
        all_tags = add_session.query(Tag).all()
        tgs = [tg for tg in all_tags if tg.id in tag_ids]
        post = Post(title=form.title.data, content=form.content.data, tags=tgs)
        current_user.posts.append(post)
        add_session.commit()
        return redirect('/')

    return render_template('post_add.html', title='Добавление поста', form=form)


@app.route('/post_delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_delete(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == post_id, Post.user == current_user).first()

    if post:
        db_sess.delete(post)
        db_sess.commit()
    else:
        abort(404)

    return redirect('/')


@app.route('/post/<int:post_id>/add_message', methods=['GET', 'POST'])
@login_required
def add_message(post_id):
    form = MessageForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == post_id).first()
        if not post:
            abort(404)
        thread_message = ThreadMessage()
        thread_message.content = form.content.data
        thread_message.user = current_user
        db_sess.commit()
        post.thread_messages.append(thread_message)

        db_sess.commit()
        return redirect('/')

    return render_template('message_add.html', form=form)


@app.route("/vote/<int:post_id>", methods=["POST"])
def vote(post_id: int):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    if request.form.get("upvote"):
        post.rating += 1
    elif request.form.get("downvote"):
        post.rating -= 1
    db_sess.commit()
    return redirect('/')


@app.route("/complete/<int:post_id>", methods=["GET", "POST"])
def set_completed(post_id: int):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    post.done = True
    db_sess.commit()
    return redirect('/')


@app.route("/")
def index():
    session = db_session.create_session()
    posts = session.query(Post).order_by(Post.done, desc(Post.rating), desc(Post.created_date))
    return render_template("index.html", posts=posts, tag=None)


@app.route("/<int:tag_id>")
def index_with_tag(tag_id):
    session = db_session.create_session()
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    posts = [x for x in session.query(Post).order_by(Post.done, desc(Post.rating), desc(Post.created_date)) if
             tag in x.tags]
    return render_template("index.html", posts=posts, tag=tag)


@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = EditPostForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == post_id, Post.user == current_user).first()

        if post:
            form.title.data = post.title
            form.content.data = post.content
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == post_id, Post.user == current_user).first()

        if post:
            post.title = form.title.data
            post.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)

    return render_template('posts.html', title='Редактирование новости', form=form)


if __name__ == '__main__':
    db_session.global_init("db/database.sqlite", app)
    app.run(debug=False, port=os.getenv("PORT", default=5000), host='0.0.0.0')
