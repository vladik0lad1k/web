from flask import Flask, request
import sqlite3
from data import db_session
from data.users import User

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()
__factory = None
app = Flask(__name__)


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


if __name__ == '__main__':
    db_session.global_init("database/db.db")
    app.run(port=8080, host='127.0.0.1')

