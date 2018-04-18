# coding:utf-8
from iHome.api_1_0 import api
from iHome import redis_store


@api.route('/', methods=['GET', 'POST'])
def index():
    redis_store.set('name', 'zxc')
    return 'Hello World!'
