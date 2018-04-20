# coding:utf-8
import logging
import redis

configs = dict()


def route(url):
    def func1(func):
        # 添加键值对，key是需要访问的url，value是当这个url需要访问的时候，需要调用的函数引用
        configs[url] = func

        def func2(*args, **kwargs):
            return func(*args, **kwargs)

        return func2

    return func1


class Config(object):
    """工程配置信息"""
    SECRET_KEY = "GApcR/AkqKg3/ujZ/SmEfmnsLWQvyqBFN2ZrSrfooktzd0GL4JylkoVAIikGUML6"

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期为1天，单位是秒


@route('dev')
class Development(Config):
    """开发模式下的配置"""
    # 调试级别
    LOGGING_LEVEL = logging.DEBUG


@route('pro')
class Production(Config):
    """生产环境,线上,部署之后"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome'
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期为1天，单位是秒

    LOGGING_LEVEL = logging.WARN

@route('unit')
class UnitTest(Config):
    """单元测试配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_test'


# print configs

