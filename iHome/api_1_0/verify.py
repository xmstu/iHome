# coding:utf-8
# 图片验证和短信验证
import logging

from flask import make_response, jsonify
from flask import request

from iHome import constants
from iHome import redis_store
from iHome.utils.response_code import RET
from . import api
from iHome.utils.captcha.captcha import captcha

prev_image_uuid = ''


@api.route('/image_code', methods=['GET'])
def get_image_code():
    """提供图片验证码"""
    # 1.获取uuid,并校验uuid
    # 2.生成图片验证码
    # 3.使用redis数据库缓存图片验证码,uuid作为key
    # 4.响应图片验证码

    # 1.获取之前的uuid和当前的uuid

    # 2.生成图片验证码
    name, text, image = captcha.generate_captcha()

    # 3.使用redis数据库缓存图片验证码,uuid作为key
    try:
        # 删除之前的
        if prev_image_uuid:
            redis_store.delete('ImageCode:%s' % prev_image_uuid)

        cur_image_uuid = request.args.get('cur')

        global prev_image_uuid
        prev_image_uuid = cur_image_uuid

        # 保存当前的
        redis_store.setex('ImageCode:%s' % cur_image_uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        logging.error(e)
        # 返回响应内容
        return make_response(jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败'))

    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    # 4.响应图片验证码
    return resp