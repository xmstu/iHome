# coding:utf-8
# 程序入口

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


class Config(object):
    """"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS


app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.S


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(port=5003, debug=True)
