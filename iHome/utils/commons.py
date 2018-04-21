# coding:utf-8
# 通用设施文件(正则url、登录验证装饰器)
from functools import wraps

from flask import g
from flask import session, jsonify
from werkzeug.routing import BaseConverter

from iHome.utils.response_code import RET


class RegexConverter(BaseConverter):
    """自定义正则转换器"""

    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_required(view_func):
    """自定义装饰器判断用户是否登录"""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        """具体实现判断用户是否登录的逻辑"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
        else:
            g.user_id = user_id
            return view_func(*args, **kwargs)

    return wrapper