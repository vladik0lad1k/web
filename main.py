from flask import Flask, request, render_template
from data import db_session
from data.users import User
from data.news import News
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None
app = Flask(__name__, template_folder='templates')


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    user = db_sess.query(User).first()
    return user.name


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
    return render_template('add-news.html')


@app.route('/save-news')
def save_news():
    title = request.args.get('title')
    text = request.args.get('text')
    try:
        news = News()
        news.title = title
        news.content = text
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





if __name__ == '__main__':
    db_session.global_init("database/db.db")
    app.run(port=8080, host='127.0.0.1')

