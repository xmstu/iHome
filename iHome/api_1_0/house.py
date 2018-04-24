# coding:utf-8
import logging

import datetime
from flask import current_app, jsonify
from flask import g
from flask import request
from flask import session

from iHome import constants, redis_store
from iHome import db
from iHome.models import Area, House, Facility, HouseImage, Order
from iHome.utils.commons import login_required
from iHome.utils.image_storage import upload_image
from iHome.utils.response_code import RET
from . import api


@api.route('/houses/search', methods=['GET'])
def get_house_search():
    """提供搜索数据
    0.获取搜索要使用的参数
    1.无条件查询所有的房屋数据
    2.构造房屋数据
    3.响应房屋数据
    """

    # 0.获取搜索使用的参数
    aid = request.args.get('aid')
    # 获取排序规则:new根据发布时间倒序;booking:根据订单倒序;price-inc:根据价格由低到高;price-des:根据价格由高到低
    sk = request.args.get('sk')
    current_app.logger.debug(sk)
    # 获取用户要看的页码
    p = request.args.get('p')

    sd = request.args.get('sd', '')
    ed = request.args.get('ed', '')

    start_date = None
    end_date = None

    try:
        p = int(p)

        if sd:
            start_date = datetime.datetime.strptime(sd, '%Y-%m-%d')
        if ed:
            end_date = datetime.datetime.strptime(ed, '%Y-%m-%d')
        if start_date and end_date:
            assert start_date < end_date, u'入住时间有误'  # 主动抛出异常,让后面的代码可以捕获到

    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)

    # 从缓存中获取房屋列表数据
    try:
        name = 'house_list_%s_%s_%s_%s' % (aid, sd, ed, sk)
        response_dict = redis_store.hget(name, p)
        if response_dict:
            return jsonify(errno=RET.OK, errmsg='OK', data=eval(response_dict))
    except Exception as e:
        current_app.logger.error(e)

    # 1.无条件查询所有的房屋数据
    try:
        house_query = House.query
        if aid:
            house_query = house_query.filter(House.area_id==aid)

        conflict_orders = []

        if start_date and end_date:
            conflict_orders = Order.query.filter(end_date>Order.begin_date, start_date<Order.end_date).all()

        elif start_date:
            conflict_orders = Order.query.filter(start_date < Order.end_date).all()

        elif end_date:
            conflict_orders = Order.query.filter(end_date > Order.begin_date).all()

        if conflict_orders:

            conflict_houses_ids = [order.house_id for order in conflict_orders]
            house_query = house_query.filter(House.id.notin_(conflict_houses_ids))

        # 排序
        if sk == 'booking':
            house_query = house_query.order_by(House.order_count.desc())
        elif sk == 'price-inc':
            house_query = house_query.order_by(House.price.asc())
        elif sk == 'price-des':
            house_query = house_query.order_by(House.price.desc())
        else:
            house_query = house_query.order_by(House.create_time.desc())

        # 取出筛选后的所有的数据p
        # houses = house_query.all()

        # 使用分页查询指定条数的数据:参数1.要读取的页码, 参数2,是每页数据条数, 参数3,默认有错就不输出
        paginate = house_query.paginate(p, constants.HOUSE_LIST_PAGE_CAPACITY, False)
        # 获取当前页的模型对象
        houses = paginate.items
        # 获取总的页数
        total_page = paginate.pages

    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')

    # 2.构造房屋数据
    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())

    response_dict = {
        'house': house_dict_list,
        'total_page': total_page
    }

    # 缓存搜索房屋后的数据
    try:
        name = 'house_list_%s_%s_%s_%s' % (aid,sd,ed,sk)
        # 创建事务管道对象
        pipeline = redis_store.pipeline()
        # 开启事务
        pipeline.multi()

        # 开启事务后，执行redis的操作
        pipeline.hset(name, p, response_dict)
        pipeline.expire(name, constants.HOUSE_LIST_REDIS_EXPIRES)

        # 执行、提交事务即可。不需要自己参入事务额回滚
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)

    # 3.响应房屋数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_dict)


@api.route('/houses/index', methods=['GET'])
def get_house_index():
    """主页房屋推荐,推荐最新发布的5个房屋
    1.直接查询最新发布的5个房屋:根据创建的时间倒叙,取最前面的5个
    2.构造房屋推荐数据
    3.响应房屋推荐数据
    """

    #     1.直接查询最新发布的5个房屋:根据创建的时间倒序,取最前面的5个
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋推荐数据失败')

    #     2.构造房屋推荐数据
    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())

    #     3.响应房屋推荐数据
    return jsonify(errno=RET.OK, errmsg='OK', data=house_dict_list)


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

    # 尝试获取登录用户信息:有可能是未登录的
    login_user_id = session.get('user_id', -1)

    # 3.响应房屋详情数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_house_detail, login_user_id=login_user_id)


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
    # 在查询数据库之前,读取缓存的城区信息
    # eval: 会根据字符串的数据的结构,自动生成对应的对象
    try:
        area_dict_list = redis_store.get('Areas')
        if area_dict_list:
            return jsonify(errno=RET.OK, errmsg='OK', data=eval(area_dict_list))
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)

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

    # 缓存城区数据,set:存储字符串,hset:存储hash,lpush:列表
    # 非常重要的注意点:缓存时,如果出现了异常,不需要return,因为如果return了,会影响主线逻辑的正常执行
    # 缓存时附带逻辑,可有可无
    try:
        redis_store.set('Areas', area_dict_list, constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        current_app.logger.error(e)

    # 3.响应城区信息
    return jsonify(errno=RET.OK, errmsg='OK', data=area_dict_list)