# coding:utf-8
# 图片验证和短信验证
import json
import logging
import random
import re

from flask import abort
from flask import current_app
from flask import make_response, jsonify
from flask import request

from iHome import constants
from iHome import redis_store
from iHome.utils.response_code import RET
from iHome.utils.sms import CCP
from . import api
from iHome.utils.captcha.captcha import captcha


@api.route('/sms_code', methods=['POST'])
def send_sms_code():
    """发送短信验证码
    1.获取参数:手机号，验证码，uuid
    2.判断是否缺少参数，并对手机号格式进行校验
    3.获取服务器存储的验证码
    4.跟客户端传入的验证码进行对比
    5.如果对比成功就生成短信验证码
    6.调用单例类发送短信
    7.如果发送短信成功，就保存短信验证码到redis数据库
    8.响应发送短信的结果
    """

    # 1.获取参数：手机号，验证码uuid
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    imageCode_client = json_dict.get('imageCode')
    uuid = json_dict.get('uuid')

    # 2.1　验证参数是否为空
    if not all([mobile, imageCode_client, uuid]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 2.2　验证手机号码是否为合法
    if not re.match(r'^1[358]{1}\d{9}$' , mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    # 3.1　验证图片验证码是否正确
    try:
        imageCode_server = redis_store.get('ImageCode:%s' % uuid)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='查询验证码失败')
    # 3.2　验证码不存在就报错
    if not imageCode_server:
        return jsonify(errno=RET.NODATA, errmsg='验证码不存在')

    # 4.1　客户端验证码和传过来的用户自己输入的验证码进行对比
    if imageCode_client.lower() != imageCode_server.lower():
        return jsonify(errno=RET.PARAMERR, errmsg='输入的图片验证码错误')

    # 5.todo　如果对比成功就生成验证码短信
    sms_code = "%06d" % random.randint(0, 999999)
    print sms_code

    # 6.调用单例类发送短信
    # ret = CCP().send_sms_msg(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    # if ret != 1:
    #     return jsonify(errno=RET.THIRDERR, errmsg='第三方接口发送验证码失败')

    # todo 7.发送验证码成功就保存短信验证码到redis数据库中去
    try:
        redis_store.set('SMS:%s' % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES )
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='存储短信验证码失败')

    # 8.响应发送短信的结果
    return jsonify(errno=RET.OK, errmsg='发送验证码成功')


prev_image_uuid = ''


@api.route('/image_code', methods=['GET'])
def get_image_code():
    """提供图片验证码"""
    # 1.获取uuid,并校验uuid
    # 2.生成图片验证码
    # 3.使用redis数据库缓存图片验证码,uuid作为key
    # 4.响应图片验证码

    # 1.获取之前的uuid和当前的uuid
    cur_image_uuid = request.args.get('cur')
    if not cur_image_uuid:
        abort(403)

    # 2.生成图片验证码
    name, text, image = captcha.generate_captcha()
    logging.debug('验证码:%s' % text)
    # current_app.logger.debug('app验证码内容是:' + text)

    # 3.使用redis数据库缓存图片验证码,uuid作为key
    try:
        # 删除之前的验证码
        if prev_image_uuid:
            redis_store.delete('ImageCode:%s' % prev_image_uuid)

        global prev_image_uuid
        prev_image_uuid = cur_image_uuid

        # 保存当前的验证码
        redis_store.setex('ImageCode:%s' % cur_image_uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        # 返回响应内容
        return make_response(jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败'))

    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'

    # 4.响应图片验证码
    return resp