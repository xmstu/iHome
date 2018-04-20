# coding:utf-8
# 创建应用实例
import logging
from logging.handlers import RotatingFileHandler

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


def setUpLogging(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("/home/python/PycharmProjects/iHome/logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def get_app(config_name):

    # 根据开发环境设置日志等级
    setUpLogging(configs[config_name].LOGGING_LEVEL)

    app = Flask(__name__)

    app.config.from_object(configs[config_name])

    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    CSRFProtect(app)

    Session(app)

    app.url_map.converters['re'] = RegexConverter

    # 哪里注册蓝图就在哪里使用蓝图,避免某些变量还没存在就导入
    from api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/1.0')

    from web_html import html_blue
    app.register_blueprint(html_blue)

    return app

