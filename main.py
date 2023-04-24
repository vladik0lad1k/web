from flask import Flask, request, render_template, redirect
from data import db_session
from data.users import User
from data.news import News
import sqlalchemy.ext.declarative as dec
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import os

static_path = 'static'
SqlAlchemyBase = dec.declarative_base()
__factory = None
app = Flask(__name__, template_folder='templates', static_url_path='/static')

login_manager = LoginManager()
login_manager.init_app(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        print(current_user.avatar)
    return news()


@app.route('/user')
def user():
    print(request.args.get('name'))
    print(request.args.get('email'))
    try:
        user = User()
        user.name = "Пользователь 1"
        user.about = "биография пользователя 1"
        user.email = "email@email.ru"
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
    except Exception as e:
        return 'error'
    return 'ok'


@app.route('/about')
def about():
    name = request.args.get("name")
    if not name:
        name = 'Друг'
    return render_template('index.html', name=name)


@app.route('/add-news')
def add_news():
    if current_user.is_authenticated:
        return render_template('add-news.html')
    else:
        return redirect('/login')


@app.route('/save-news')
def save_news():
    title = request.args.get('title')
    text = request.args.get('text')
    try:
        news = News()
        news.title = title
        news.content = text
        news.user_id = current_user.id
        db_sess = db_session.create_session()
        db_sess.add(news)
        db_sess.commit()
    except Exception as e:
        return 'error'
    return render_template('add-news.html')


@app.route('/news')
def news():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    return render_template('news.html', news=news)


@app.route('/news/<int:id>')
def one_new(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    return render_template('one_new.html', news=news)


@app.route('/reg')
def reg():
    db_sess = db_session.create_session()
    username = request.args.get('username')
    password = request.args.get('password')
    if username and password:
        check_user = db_sess.query(User).filter(User.name == username).first()
        if check_user:
            return render_template('reg.html', message='Ошибка, пользователь уже существует')
        user = User()
        user.name = username
        user.hashed_password = password
        db_sess.add(user)
        db_sess.commit()
        return render_template('message.html', message='Пользователь создан')
    return render_template('reg.html')


class LoginForm(FlaskForm):
    name = StringField('Ник', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/avatar', methods=['GET', 'POST'])
def avatar():
    if request.method == 'GET':
        return render_template('avatar.html')
    elif current_user.is_authenticated:
        f = request.files['avatar']
        f.save('static/' + f.filename)
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.avatar = f.filename
        db_sess.commit()
        return "Форма отправлена"


@app.route('/out')
@login_required
def out():
    logout_user()
    return redirect("/")


@app.route('/profile/<int:id>')
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    news = db_sess.query(News).filter(News.user_id == id).all()
    return render_template('user_profile.html', user=user, news=news)


@app.route('/change_name', methods=['GET', 'POST'])
@login_required
def change_name():
    db_sess = db_session.create_session()
    form = NicknameForm()
    if not form.name.data:
        form.name.data = current_user.name
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.name = form.name.data
            db_sess.commit()
            return render_template('change_name.html', msg='Никнейм изменён', form=form)
    return render_template('change_name.html', form=form)


class NicknameForm(FlaskForm):
    name = StringField('Ник', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


@app.route('/users')
def users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('users.html', users=users)


@app.route('/edit-news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    msg = None
    if request.method == 'POST':
        news.title = request.form.get('title')
        news.content = request.form.get('text')
        db_sess.commit()
        msg = 'Сохранено'
    return render_template('edit-news.html', news=news, msg=msg)


@app.route('/delete-news/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_news(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    msg = None
    if request.method == 'POST':
        db_sess.delete(news)
        db_sess.commit()
        msg = 'Сохранено'
        return redirect('/news')
    return render_template('delete-news.html', news=news, msg=msg)


if __name__ == '__main__':
    db_session.global_init("database/db.db")
    app.run(port=8080, host='127.0.0.1')
