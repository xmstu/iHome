# coding:utf-8

from flask import Blueprint
from flask import current_app, make_response
from flask.ext.wtf.csrf import generate_csrf

html_blue = Blueprint('html', __name__)


@html_blue.route('/<re(r".*"):file_name>')
def get_static_html(file_name):
    """提供静态html文件"""
    # 提示:如何才能使用file_name找到对应的html文件,路径是什么
    if not file_name:
        file_name = 'index.html'

    if file_name != 'favicon.ico':
        # 拼接静态文件路径
        file_name = 'html/%s' % file_name

    # 生成csrf_token
    csrf_token = generate_csrf()
    # 将csrf_token设置到cookie中
    response = make_response(current_app.send_static_file(file_name))
    response.set_cookie("csrf_token", csrf_token)
    # 去项目路径中查找静态html文件,并响应给浏览器
    return response