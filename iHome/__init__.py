# coding:utf-8
# 创建应用实例
import redis
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from flask_session import Session
# from config import Config, Development, Production, UnitTest
from config import configs
from utils.commons import RegexConverter

# 创建db实例对象
db = SQLAlchemy()
# 定义全局的redis_store
redis_store = None


def get_app(config_name):

    app = Flask(__name__)

    app.config.from_object(configs[config_name])

    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    csrf = CSRFProtect(app)

    Session(app)

    app.url_map.converters['re'] = RegexConverter

    # 哪里注册蓝图就在哪里使用蓝图,避免某些变量还没存在就导入
    from api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')

    from web_html import html_blue
    app.register_blueprint(html_blue)

    return app

