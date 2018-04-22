# coding:utf-8
import logging

from flask import current_app, jsonify
from flask import g
from flask import request

from iHome import constants
from iHome import db
from iHome.models import Area, House, Facility, HouseImage
from iHome.utils.commons import login_required
from iHome.utils.image_storage import upload_image
from iHome.utils.response_code import RET
from . import api


@api.route('/houses/<int:house_id>', methods=['GET'])
def get_house_detail(house_id):
    """提供房屋详情数据
    1.直接查询house_id对应的房屋信息
    2.构造房屋详情数据
    3.响应房屋详情数据
    """

    # 1.直接查询house_id对应的房屋信息
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 2.构造房屋详情数据
    response_house_detail = house.to_full_dict()

    # 3.响应房屋详情数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_house_detail)


@api.route('/houses/image', methods=['POST'])
@login_required
def upload_house_image():
    """上传房屋图片
    1.接受参数:image_data, house_id, 并校验
    2.使用house_id, 查询房屋信息,只有当房屋存在时,才会上传图片
    3.调用上传图片的工具方法,上传房屋图片
    4.创建HouseImage模型对象,并保存房屋图片key，并保存到数据库
    5.响应结果
    """

    # 1.接受参数:image_data, house_id, 并校验
    try:
        image_data = request.files.get('house_image')
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='获取图片失败')
    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少必传参数')

    # 2.使用house_id, 查询房屋信息,只有当房屋存在时,才会上传图片
    try:
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    # 3.调用上传图片的工具方法,上传房屋图片
    try:
        key = upload_image(image_data)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

    # 4.创建HouseImage模型对象,并保存房屋图片key，并保存到数据库
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = key

    # 给房屋设置默认的图片
    if not house.index_image_url:
        house.index_image_url = key

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片失败')

    # 5.响应结果
    house_image_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传图片成功', data={'house_image_url': house_image_url})


@api.route('/houses', methods=['POST'])
@login_required
def pub_house():
    """发布新房源
    0.判断是否登录
    1.接受参数:基本信息和设备信息
    2.判断参数是否为空,并对某些参数进行合法性的校验,比如金钱相关的
    3.创建房屋模型对象,并赋值
    4.保存房屋数据到数据库
    5.响应发布新的房源的结果
    """

    # 1.接受参数:基本信息和设备信息
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')

    # 2.判断参数是否为空,并对某些参数进行合法性的校验,比如金钱相关的
    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    # 校验价格和押金参数是否合法,不允许传入数字以外的数据 10.1元 * 100 ==> 1010分
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='金额格式错误')

    # 3.创建房屋模型对象,并赋值
        # 设置数据到模型
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    facility = json_dict.get('facility')
    if facility:
        facilities = Facility.query.filter(Facility.id.in_(facility)).all()
        house.facilities = facilities

    # 4.保存房屋数据到数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋数据失败')

    # 5.响应发布新的房源的结果
    return jsonify(errno=RET.OK, errmsg='发布房源数据成功', data={'house_id':house.id})


@api.route('/areas', methods=['GET'])
def get_area():
    """提供城区信息
    1.直接查询所有城区信息
    2.构造城区信息响应数据
    3.响应城区信息

    """

    # 1.直接查询所有城区信息
    try:
        areas = Area.query.all()
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询城区信息失败')

    # 2.构造城区信息响应数据
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())

    # 3.响应城区信息
    return jsonify(errno=RET.OK, errmsg='OK', data=area_dict_list)