# coding:utf-8
# 创建应用实例
import redis
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from flask_session import Session
# from config import Config, Development, Production, UnitTest
from config import configs

# 创建db实例对象
db = SQLAlchemy()


def get_app(config_name):

    app = Flask(__name__)

    app.config.from_object(configs[config_name])

    db.init_app(app)

    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    csrf = CSRFProtect(app)

    Session(app)

    return app