# coding:utf-8
from iHome.api_1_0 import api


@api.route('/', methods=['GET', 'POST'])
def index():
    return 'Hello World!'
