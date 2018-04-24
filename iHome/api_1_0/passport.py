# coding:utf-8
# 登录注册
import json
import re

import logging
from flask import current_app
from flask import request, jsonify
from flask import session

from iHome import redis_store, db
from iHome.models import User
from iHome.utils.response_code import RET
from . import api


@api.route('/users', methods=['POST'])
def register():
    """注册
    1.获取注册参数：手机号，短信验证码，密码
    2.判断参数是否缺少
    3.获取服务器存储的短信验证码
    4.与客户端传入的短信验证码对比
    5.如果对比成功，就创建用户模型User对象，并给属性赋值
    6.将模型属性写入到数据库
    7.响应注册结果
    """

    # 1.获取注册参数：手机号，短信验证码，密码
    # json_str = request.data
    # json_dict = json.loads(json_str)

    json_dict = request.get_json()
    mobile = json_dict.get('mobile')
    sms_code_client = json_dict.get('sms_code')
    password = json_dict.get('password')

    # 2.判断参数是否缺少
    if not all([mobile, sms_code_client, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 手机格式
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    # 检测手机号是否注册过
    if User.query.filter(User.mobile == mobile).first():
        return jsonify(errno=RET.DATAEXIST, errmsg='该手机号已存在')

    # 3.获取服务器存储的短信验证码
    try:
        sms_code_server = redis_store.get('SMS:%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询短信验证码失败')
    if not sms_code_server:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码不存在')

    # 4.与客户端传入的短信验证码对比
    if sms_code_client != sms_code_server:
        return jsonify(errno=RET.PARAMERR, errmsg='短信验证码输入有误')

    # 5.如果对比成功，就创建用户模型User对象，并给属性赋值
    user = User()
    user.mobile = mobile
    user.name = mobile
    user.password = password

    # 6.将模型属性写入到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存用户数据失败')

    # 注册即登录，也就是保存注册时生成的数据
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    # 7.响应注册结果
    return jsonify(errno=RET.OK, errmsg='注册成功')


@api.route('/session', methods=['GET'])
def check_login():

    name = session.get('name')
    user_id = session.get('user_id')

    try:
        nickname = User.query.get(user_id).name
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库失败')

    if not name:
        return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    else:
        return jsonify(errno=RET.OK, errmsg='用户已登录', data={'name':nickname, 'user_id':user_id})


@api.route('/session', methods=["POST"])
def login():
    """
    1.获取参数
    2.判断参数是否有值
    3.判断手机号是否合法
    4.查询数据库用户信息
    5.用户不存在判断
    6.校验密码
    7.使用session保存用户信息
    :return:
    """

    # 1.获取参数
    dict_json = request.get_json()
    mobile = dict_json.get('mobile')
    password = dict_json.get('password')

    # 2.判断参数是否有值
    if not all([dict_json, mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 3.判断手机号是否合法
    if not re.match(u"^1[34578]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 4.查询数据库用户信息
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')

    # 5.用户不存在判断
    if user is None:
        return jsonify(errno=RET.USERERR, errmsg='用户或密码错误')

    # 6.校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.LOGINERR, errmsg='用户或密码错误')

    # 7.使用session保存用户信息
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['name'] = user.name

    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/session', methods=["DELETE"])
def logout():
    session.pop('name', None)
    session.pop('mobile', None)
    session.pop('user_id', None)
    return jsonify(errno=RET.OK, errmsg='OK')

